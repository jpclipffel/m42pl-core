import logging
from contextlib import ExitStack, AsyncExitStack
import asyncio
import inspect
import itertools

from typing import Dict, List, Generator

import m42pl
from m42pl import errors
from m42pl.event import Event
from m42pl.context import Context
from m42pl.commands import (
    GeneratingCommand,
    StreamingCommand,
    BufferingCommand,
    MetaCommand,
    MergingCommand
)


class Pipeline:
    """Manages and runs a list of M42PL commands.
    """

    @classmethod
    def from_dict(cls, data: dict) -> object:
        """Returns a new :class:`Pipeline` from a :class:`dict`.

        The source map :param:`data` must match with the following map:

            {
                'commands': [               # Commands list
                    {
                        'alias': '...',     #       Command alias
                        'args': [],         #       Command arguments
                        'kwargs': {}        #       Command kwarg
                    },
                    # ...
                ]
            }

        **Important**: This function does not invoke the commands'
        `__new__` method: this means that :param:`dc` must have been
        generated from an already built pipeline, i.e. whoms commands
        have been instanciated.
        The underlying reason is that commands may overload their 
        `__new__` method to return more than one class instance.
        
        :param data:  Source pipeline as :class:`dict`
        """
        # Build the commands list
        commands = []
        for command in data['commands']:
            commands.append(object.__new__(m42pl.command(command['alias'])))
            commands[-1].__init__(*command.get('args', []), **command.get('kwargs', {}))
        # Remove original commands list from dict
        data.pop('commands')
        # Builds and returns a new pipeline
        # return cls( { **{'commands': commands}, **dc} )
        return cls(commands=commands)

    @staticmethod
    def flatten_commands(commands) -> Generator:
        """Flatten the list of commands.

        This is necessary as some commands `__new__` may returns more
        than one class instance.
        """
        for command in commands:
            if isinstance(command, (tuple, list)):
                yield from Pipeline.flatten_commands(command)
            else:
                yield command

    def __init__(self, commands: list = [], context: Context = None,
                 distributable: bool = True, name: str = 'lambda',
                 timeout: float = 0) -> None:
        """
        :param commands:        Pipeline's commands list.
        :param context:         Pipeline's context.
        :param kvstore:         Pipeline's KV store instance.
        :param distributable:   True if the pipeline execution can be distributed, False otherwise.
        :param name:            Pipeline's name.
        :param timeout:         Generator timeout in seconds.
                                If the pipeline's generator didn't yiled event before :param:`timeout` seconds,
                                the other commands are 'waked up' to force buffered events to be processed.
        
        :ivar logger:           Logger instance.
        :ivar chunk:            Current chunk number.
        :ivar chunks:           Total chunks count.
        :ivar metas:            Leading meta commands.
        :ivar generator:        Generating command.
        :ivar processors:       Processing commands (any but generator)
        """
        self.context = context
        self.distributable = distributable
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(name=f'm42pl.pipeline.{name}')
        self.chunk, self.chunks = 1, 1
        # ---
        # Set commands list and build
        self.commands = commands
        self.build()
        # ---
        # Pipeline state
        self._commands_set = False
        self._ready = True

    def to_dict(self) -> Dict:
        """Returns a represention of the current pipeline as a JSON-serializable :class:`dict`.
        
        A new :class:`Pipeline` object can be created from this dict using :meth:`from_json`.
        """
        return {
            'commands': [ c.to_dict() for c in self.commands ],
            'distributable': self.distributable,
            'name': self.name,
            'timeout': self.timeout
        }

    def set_chunk(self, chunk: int = 0, chunks: int = 1) -> None:
        """Set pipeline and pipeline's commands chunk and chunks count.
        
        :param chunk:   Current chunk number. Starts at `0`.
        :param chunks:  Total chunks count. Minimum is `1`.
        """
        self.chunk, self.chunks = chunk, chunks
        for command in self.commands:
            command.set_chunk(chunk, chunks)

    def build(self):
        """(Re)builds the pipeline.
        """
        self.logger.info(f'building pipeline: pipeline="{self.name}"')
        # ---
        # Initialize commands sets
        self.metas = []
        self.generator = None
        self.processors = []
        # ---
        # Build commands blocks
        self.commands = list(Pipeline.flatten_commands(self.commands))
        for i, command in enumerate(self.commands):
            # Heading meta commands
            if isinstance(command, MetaCommand) and self.generator is None:
                self.logger.info(f'Adding command to metas')
                self.metas.append(command)
            # Generating command
            elif isinstance(command, GeneratingCommand):
                if self.generator is not None:
                    raise Exception(f'Command #{i}: Could not add another generating command')
                else:
                    self.generator = command
            # Processing commands
            else:
                if self.generator is None:
                    self.logger.info('Pipeline does not start with a generator: adding "echo" as default generator')
                    self.generator = m42pl.command('echo')()
                self.processors.append(command)

    def get_pipeline(self, name: str):
        """Get a pipeline by name from the internal context.

        :param name:    Pipeline name, optionally starting with '@'.
        """
        return self.context.pipelines[name.lstrip('@')]

    async def _setup_commands(self, event):
        """Setup the commands (aka. commands post-initialization).

        Some commands' internals (e.g. fields) may requires access to
        the pipeline (and nested objects such as context or parents
        and children pipelines) to finish their initialization.

        :param event:       Latest received event (may be `None`).
        """
        if not self._commands_set:
            self.logger.debug(f'setting-up pipeline commands: pipeline="{self.name}"')
            for command in self.commands:
                # Override command logger
                command.logger = self.logger.getChild(
                    command.__class__.__name__
                )
                # Setup command
                try:
                    await command.setup(event=event, pipeline=self)
                except Exception as error:
                    if not isinstance(error, errors.M42PLError):
                        raise errors.CommandError(command, message=str(error))
                    else:
                        raise error
            # Do not re-setup commands (needed for sub pipelines)
            self._commands_set = True
        else:
            self.logger.debug(f'pipeline commands already set: pipeline="{self.name}"')

    async def _run_commands(self, commands, event, ending, remain):
        """Runs a commands list.

        :param commands:    Commands list.
        :param event:       Current event.
        :param ending:      `True` if the pipeline is ending,
                            `False` otherwise.
        :param remain:      Amount or remaining events in the previous
                            command.
        """
        if len(commands):
            # Current command instance and children commands
            command, has_further_commands = commands[0], len(commands) > 1
            # print(f'{command} -> call')
            # Run command and children commands
            async for _event in command(event=event, pipeline=self, ending=ending, remain=remain):
                # print(f'{command} -> got event, continue with new event')
                if has_further_commands:
                    async for __event in self._run_commands(commands[1:], _event, ending, (remain + await command.remain())):
                        yield __event
                elif _event:
                    yield _event
            else:
                if ending:
                    # print(f'{command} -> got no event, continue with last event')
                    if has_further_commands:
                        async for _event in self._run_commands(commands[1:], None, ending, remain):
                            yield _event
                    elif event:
                        yield event

    def stop(self):
        """Stops the pipeline.
        """
        self._ready = False

    async def __call__(self, event: Event = None):
        """Runs the pipeline.

        The pipeline is ran in two or more iterations:

        * At first, events are processed as they are generated
        * At last AND when the pipeline's generating command times out,
          the pipeline's commands are *awakened* to force them to yield
          their buffered events.

        :param event:   Initial event (may be `None`)
        """
        # ---
        # Prepare source event
        event = event or Event()
        # ---
        # Control pipeline structure
        if not self.generator:
            self.logger.debug(f'ignoring pipeline: reason="no generator", pipeline="{self.name}"')
            yield event
            return
        # ---
        # Setup commands
        await self._setup_commands(event)
        # ---
        # Run pipeline
        self.logger.debug(f'entering commands contexts: pipeline="{self.name}"')
        async with AsyncExitStack() as stack:
            metas = [await stack.enter_async_context(cmd) for cmd in self.metas]
            generator = await stack.enter_async_context(self.generator)
            processors = [await stack.enter_async_context(cmd) for cmd in self.processors]
            # ---
            self.logger.info(f'running pipeline metas: pipeline="{self.name}"')
            async for _ in self._run_commands(commands=metas, event=event, ending=False, remain=0):
                pass
            # ---
            itr = generator(event=event, pipeline=self).__aiter__()
            self.logger.info(f'starting pipeline: pipeline="{self.name}"')
            while True:
                # Generate event
                try:
                    if self.timeout > 0:
                        task = asyncio.create_task(itr.__anext__())
                        event = await asyncio.wait_for(asyncio.shield(task), self.timeout)
                    else:
                        event = await itr.__anext__()
                except asyncio.TimeoutError:
                    self.logger.debug(f'generator timeout, forcing pipeline wakeup: pipeline="{self.name}"')
                    async for e in self._run_commands(commands=processors, event=None, ending=False, remain=0):
                        yield e
                    event = await task
                except StopAsyncIteration:
                    self.logger.debug(f'received StopAsyncIteration, breaking pipeline loop: pipeline="{self.name}"')
                    break
                # Process event
                if len(processors):
                    async for e in self._run_commands(commands=processors, event=event, ending=False, remain=0):
                        yield e
                else:
                    yield event
                # Control state
                if not self._ready:
                    self.logger.debug(f'pipeline state switched to not ready, breaking pipeline loop: pipeline="{self.name}')
                    break
            # ---
            # Process buffered events
            self.logger.debug(f'terminating pipeline: pipeline="{self.name}"')
            self.ending = True
            if len(processors):
                self.logger.info(f'running pipeline processors in end mode: pipeline="{self.name}"')
                async for e in self._run_commands(commands=processors, event=None, ending=True, remain=0):
                    yield e
        # ---
        # Done
        self.logger.debug(f'finished pipeline: pipeline="{self.name}"')
