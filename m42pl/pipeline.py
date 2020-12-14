import logging
from contextlib import ExitStack, AsyncExitStack
import asyncio
import inspect

from typing import Dict, List, Generator

import m42pl
from m42pl.event import Event
from m42pl.context import Context
from m42pl.commands import GeneratingCommand, StreamingCommand, BufferingCommand, MetaCommand, MergingCommand


class Pipeline:
    '''Holds and runs a list of m42pl commands.
    '''

    @classmethod
    def from_dict(cls, dc: dict) -> object:
        """Builds and returns a new :class:`Pipeline` from a :class:`dict`.

        This function does not invoke the commands' `__new__` method: the source pipeline
        must be already build.
        
        :param dc:  Source pipeline as :class:`dict`
        """
        # Build the commands list
        commands = []
        for command in dc['commands']:
            commands.append(object.__new__(m42pl.command(command['alias'])))
            commands[-1].__init__(*command.get('args', []), **command.get('kwargs', {}))
        # Remove original commands list from dict
        dc.pop('commands')
        # Builds and returns a new pipeline
        # return cls( { **{'commands': commands}, **dc} )
        return cls(commands=commands)

    @staticmethod
    def flatten_commands(commands) -> Generator:
        '''Flatten a list of (potentially nested) commands.

        Commands whoms `__new__` returns more than one object have their
        objects run in order.
        '''
        for command in commands:
            if type(command) in [ tuple, list ]:
                yield from Pipeline.flatten_commands(command)
            else:
                yield command

    def __init__(self, commands: list = [], context: Context = None, 
                 distributable: bool = True, name: str = 'lambda',
                 timeout: float = 0) -> None:
        """
        :param commands:        Pipeline's commands list.
        :param context:         Pipeline's context.
        :param distributable:   True if the pipeline execution can be distributed, False otherwise.
        :param name:            Pipeline's name.
        :param timeout:         Generator timeout in seconds.
                                If the pipeline's generator didn't yiled event before :param:`timeout` seconds,
                                the other commands are 'waked up' to force buffered events to be processed.
        
        :ivar chunk:            Current chunk number.
        :ivar chunks:           Total chunks count.
        :ivar generator:        Generating command.
        :ivar processors:       Streaming and meta commands.
        """
        self.context = context
        self._distribulate = distributable
        self.name = name
        self._timeout = timeout
        self._logger = logging.getLogger(name=f'm42pl.pipeline.{name}')
        self._chunk, self._chunks = 1, 1
        # ---
        # Build commands list.
        # Commands's :meth:`__new__` may return more than one object.
        # :meth:`flatten_commands` takes care of returning commands in proper order.
        self._commands = list(Pipeline.flatten_commands(commands))
        # ---
        # Pipeline state
        self._commands_set = False

    def to_dict(self) -> Dict:
        """Returns a represention of the current pipeline as a JSON-serializable :class:`dict`.
        
        A new :class:`Pipeline` object can be created from this dict using :meth:`from_json`.
        """
        return {
            'commands': [ c.to_dict() for c in self._commands ],
            'distributable': self._distribulate,
            'name': self.name,
            'timeout': self._timeout
        }

    def set_chunk(self, chunk: int = 0, chunks: int = 1) -> None:
        """Set pipeline and pipeline's commands chunk and chunks count.
        
        :param chunk:   Current chunk number. Starts at `0`.
        :param chunks:  Total chunks count. Minimum is `1`.
        """
        self._chunk, self._chunks = chunk, chunks
        for command in self._commands:
            # print (f'setting command chunk: comand="{command}", chunk={chunk}, chunks={chunks}')
            command.set_chunk(chunk, chunks)

    def prepend_commands(self, commands: list) -> None:
        """Preppend commands to the commands list.

        :param commands:    Commands list to prepend.
        """
        for command in reversed(list(Pipeline.flatten_commands(commands))):
            self._commands.insert(0, command)

    def append_commands(self, commands: list) -> None:
        """Append commands to the comands list.
        
        :param commands:    Commands list to append.
        """
        for command in Pipeline.flatten_commands(commands):
            self._commands.append(command)

    def derive(self, commands: list = []) -> 'Pipeline':
        """Returns a duplicated :class:`Pipeline` with the given
        :param:`commands`.

        :param commands:    New commmands list.
        """
        return Pipeline(commands, self._distribulate, self.name, self._timeout)
    
    def split_by_type(self, cmd_type: type, cmd_single: bool = False) -> Generator['Pipeline', None, None]:
        """Split pipeline at each command :param:`cmdtype`.

        If :param cmd_single: is `True`, each command of the given type
        :param cmd_type: is isolated in its own pipeline. Otherwise,
        they are put as leading command in their pipeline, followed by
        the next(s) command(s).

        :param cmd_type:    Split pipeline at these command type.
        :param cmd_single:  If true, isolate each command of the given
                            type into its own pipeline. Defaults to
                            False.
        """
        pipelines = []
        for command in self._commands:
            if not isinstance(command, cmd_type):
                if len(pipelines) < 1:
                    pipelines.append(self.derive())
                pipelines[-1].append_commands([command,])
            else:
                pipelines.append(self.derive([command,]))
                if cmd_single:
                    pipelines.append(self.derive())
        return pipelines

    # def __override_command_logger(self):
    #     '''Replaces each command :instance_attribute:`Command.logger`.
    #     '''
    #     for _, command in enumerate(self.commands):
    #         command.logger = self.logger.getChild(command.__class__.__name__)

    async def _setup_commands(self, commands, event):
        '''Setup the commands (aka. post-initialization).

        Some commands' internals (e.g. fields) may requires access to
        the pipeline (and nested objects such as context or parents
        and children pipelines) to finish their initialization.

        :param commands:    Commands list.
        :param event:       Latest received event (may be `None`).
        '''
        if not self._commands_set:
            for command in commands:
                # Override command logger
                command.logger = self._logger.getChild(
                    command.__class__.__name__
                )
                # Setup command
                await command.setup(event=event or Event(), pipeline=self)
            # Do not re-setup commands (needed for sub pipelines)
            self._commands_set = True

    async def __run_commands(self, commands, event, ending, remain):
        '''Runs a commands list.

        :param commands:    Commands list.
        :param event:       Current event.
        :param ending:      `True` if the pipeline is ending,
                            `False` otherwise.
        :param remain:      Amount or remaining events in the previous
                            command.
        '''
        if len(commands):
            # Current command instance and children commands
            command, has_further_commands = commands[0], len(commands) > 1
            # Run command and children commands
            async for _event in command(event=event, pipeline=self, ending=ending, remain=remain):
                if has_further_commands:
                    async for __event in self.__run_commands(commands[1:], _event, ending, (remain + await command.remain())):
                        yield __event
                else:
                    if _event:
                        yield _event

    async def __call__(self, event: Event = None):
        '''Runs the pipeline.

        The pipeline is ran in two or more iterations:

        * At first, events are processed as they are generated
        * At last AND when the generating command (`generator`) time out, the buffering commands (:class:`BufferingCommands` and descendants)
          are *awakened* to force them to yield their buffered events

        :param event:   Initial event (may be `None`)
        '''
        if len(self._commands) < 1:
            yield event
            return
        # Setup commands
        await self._setup_commands(self._commands, event)
        # ---
        async with AsyncExitStack() as stack:
            generator = await stack.enter_async_context(self._commands[0])
            if len(self._commands) > 1:
                processors = [ await stack.enter_async_context(cmd) for cmd in self._commands[1:] ]
            else:
                processors = []
            # ---
            # print (f'run stream')
            itr = generator(event=event or Event(), pipeline=self).__aiter__()
            # task = None
            while True:
                # ---
                # Generate event
                try:
                    if self._timeout > 0:
                        task = asyncio.create_task(itr.__anext__())
                        event = await asyncio.wait_for(asyncio.shield(task), self._timeout)
                    else:
                        event = await itr.__anext__()
                except asyncio.TimeoutError:
                    # print(f'would wake up the commands pipeline !')
                    async for e in self.__run_commands(commands=processors, event=None, ending=False, remain=0):
                        yield e
                    # print(f'continue waiting for new event')
                    event = await task
                except StopAsyncIteration:
                    # print(f'done generating')
                    break
                # ---
                # TEST / Generate event
                # try:
                #     event = await itr.__anext__()
                # except Exception:
                #     break
                # ---
                # Process event
                if len(processors):
                    # print(f'processing')
                    async for e in self.__run_commands(commands=processors, event=event, ending=False, remain=0):
                        yield e
                else:
                    yield event
            # ---
            # Process buffered events
            self.ending = True
            if len(processors):
                # print(f'run ending')
                async for e in self.__run_commands(commands=processors, event=None, ending=True, remain=0):
                    yield e
                    pass
            # else:
            #     yield event
