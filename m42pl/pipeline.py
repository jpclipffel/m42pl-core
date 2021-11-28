from __future__ import annotations

from typing import TYPE_CHECKING, Generator, AsyncGenerator, Tuple, Dict, List

if TYPE_CHECKING:
    from m42pl.context import Context

import logging
from contextlib import ExitStack, AsyncExitStack
import asyncio
import inspect
import itertools
import signal

import m42pl
from m42pl import errors
from m42pl.commands import (
    Command,
    GeneratingCommand,
    StreamingCommand,
    BufferingCommand,
    MetaCommand,
    MergingCommand
)
from m42pl.event import Event


class Pipeline:
    """Holds a list of commands.

    :ivar mode:     'iterator' or 'event'
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
        `__new__` method: this means that :param:`data` must have been
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

    def __init__(self, commands: list = [], name: str = 'main') -> None:
        """
        :param commands:        Commands list
        :param name:            Pipeline name

        :ivar logger:           Logger instance
        :ivar chunk:            Current chunk number
        :ivar chunks:           Total chunks count
        :ivar pipeline_refs:    Sub-pipelines references
        :ivar metas:            Leading meta commands
        :ivar generator:        Generating command
        :ivar processors:       Processing commands (any but generator)
        """
        self.commands = commands
        self.name = name
        self.logger = logging.getLogger(name=f'm42pl.pipeline.{name}')
        self.chunk, self.chunks = 1, 1
        self.pipelines_ref: list[str] = []
        # Build
        self.build()
        # ---
        # Pipeline state
        self._commands_set = False
        self._ready = True

    def trace(self, memo: int, message: str):
        """Debug method.

        TODO: Remove.
        """
        print(f'{"." * memo * 2} {self.name}: {message}')
        return memo

    def to_dict(self) -> Dict:
        """Serializes the pipeline as a :class:`dict`.

        Ther returned :class:`dict` is JSON-serializable and a new
        :class:`Pipeline` instance can be created from it using
        :meth:`from_dict`.
        """
        return {
            'name': self.name,
            'commands': [
                command.to_dict()
                for command
                in self.commands
                if command is not None
            ]
        }

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
        # Build commands sets
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
                # if self.generator is None:
                #     self.logger.info('Pipeline does not start with a generator: adding "echo" as default generator')
                #     self.generator = m42pl.command('echo')()
                self.processors.append(command)
        # Rewrite commands list
        self.commands = list(filter(None, self.metas + [self.generator,] + self.processors))

    def set_chunk(self, chunk: int = 0, chunks: int = 1) -> None:
        """Set pipeline and pipeline's commands chunk and chunks count.
        
        :param chunk:   Current chunk number. Starts at `0`.
        :param chunks:  Total chunks count. Minimum is `1`.
        """
        self.chunk, self.chunks = chunk, chunks
        for command in self.commands:
            # command.set_chunk(chunk, chunks)
            command.chunk = (chunk, chunks)

    async def _setup_commands(self, event):
        """Setup the commands list (commands post-initialization).

        Some commands' internals (e.g. fields) may requires access to
        the pipeline (and nested objects such as context or parents
        and children pipelines) to finish their initialization.

        Once set, the commands are **not** set again event if this
        method is called more than once.

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

        :param commands:    Commands list
        :param event:       Current event
        :param ending:      `True` if the pipeline is ending,
                            `False` otherwise
        :param remain:      Amount or remaining events in the previous
                            command
        """
        if len(commands):
            # Current command instance and children commands
            command, has_further_commands = commands[0], len(commands) > 1
            # Run command and children commands
            async for _event in command(event=event, pipeline=self, ending=ending, remain=remain):
                if has_further_commands:
                    async for __event in self._run_commands(commands[1:], _event, ending, (remain + await command.remain())):
                        yield __event
                elif _event:
                    yield _event
            else:
                if ending:
                    if has_further_commands:
                        async for _event in self._run_commands(commands[1:], None, ending, remain):
                            yield _event
                    elif event:
                        yield event

    def stop(self, *args, **kwargs):
        """Stops the pipeline.
        """
        self._ready = False
        raise StopAsyncIteration('SINGINT')

    async def __call__(self, context: Context = None, event: dict|None = None,
                        infinite: bool = False, timeout: float = 0.0):
        """Runs the pipeline.

        The pipeline is ran in two or more iterations:

        * At first, events are processed as they are generated
        * At last AND when the pipeline's generating command times out,
          the pipeline's commands are *awakened* to force them to yield
          their buffered events.

        :param context:     Pipeline context
        :param event:       Initial event
        :param infinite:    Run in infinite mode (continuously receives
                            next event from calling function)
        :param timeout:     Timeout; Defaults to 0
        
        :ivar metas:        Meta commands
        :ivar generator:    Generator command
        :ivar processors:   Processing commands
        :ivar iterator:     Generator's iterator
        """
        # Setup signal handler
        signal.signal(signal.SIGINT, self.stop)

        # Setup context
        self.context = context
        # ---
        # Setup commands
        await self._setup_commands(event or Event())
        # ---
        # Enter pipeline context
        async with AsyncExitStack() as stack:
            self.logger.debug(f'entering commands contexts: pipeline="{self.name}"')
            # Enter commands context
            metas = [await stack.enter_async_context(cmd) for cmd in self.metas]
            generator = self.generator and await stack.enter_async_context(self.generator) or None
            processors = [await stack.enter_async_context(cmd) for cmd in self.processors]
            # Run pipeline metas
            self.logger.info(f'running pipeline metas: pipeline="{self.name}"')
            async for _ in self._run_commands(commands=metas, event=event, ending=False, remain=0):
                pass
            # ---
            # Setup the events iterator, i.e. the pipeline generator
            #
            # If the pipeline run in infinite mode, the initial event will
            # be received later, and the iterator will be set at the same time.
            if infinite:
                # self.trace(1, 'infinite mode: set iterator to None')
                iterator = None
            # Otherwise, set the iterator immediately.
            else:
                # self.trace(1, 'standard mode: set iterator from generator')
                iterator = generator and generator(event=event, pipeline=self).__aiter__() or None
            # ---
            # Start pipeline loop
            next_event = event
            while self._ready:
                # self.trace(2, 'looping')
                try:
                    # ---
                    # If pipeline runs in infinite mode and, it receive its
                    # next event from the calling function. The iterator is
                    # (re)set right after.
                    if infinite and not iterator:
                        # self.trace(3, f'pipeline is infinite, iterator is None: yield for initial event')
                        next_event = yield
                        # self.trace(3, f'initial event: {next_event and next_event.signature or None}')
                        if next_event:
                            # self.trace(4, f'initial event is not None, reset iterator on it')
                            iterator = generator and generator(event=next_event, pipeline=self).__aiter__() or None
                        # else:
                        #     self.trace(4, f'initial event is None, pipeline should raise StopAsyncIteration right after')
                    # ---
                    # If the pipeline has a generating command derived into an
                    # iterator, it retrieves its next event from this iterator.
                    if iterator:
                        # self.trace(3, f'iterator is set, await next event')
                        if timeout > 0.0:
                            task = asyncio.create_task(iterator.__anext__())
                            # self.trace(4, f'task shiedled: {task}')
                            next_event = await asyncio.wait_for(asyncio.shield(task), timeout)
                        else:
                            next_event = await iterator.__anext__()
                    # ---
                    # If neither the calling function nor the generator had 
                    # yield an event, stop the iteration.
                    if next_event is None:
                        self.logger.info(f'next_event is None, breaking: pipeline="{self.name}"')
                        # self.trace(3, f'next event is None, raise StopAsyncIteration')
                        raise StopAsyncIteration()
                # ---
                # Timeout occurs when the iterator took too long to yield an
                # event. Send None to the processors to 'wake-up' the
                # buffering commands and process the buffered events.
                except asyncio.TimeoutError:
                    self.logger.debug(f'generator timeout, forcing pipeline wakeup: pipeline="{self.name}"')
                    # self.trace(4, f'shielded task {task} -> wake up !')
                    async for e in self._run_commands(commands=processors, event=None, ending=False, remain=0):
                        yield e
                    next_event = await task # type: ignore
                # ---
                # StopAsyncIteration occurs when either the iterator or the
                # calling function have finished to produce events.
                except StopAsyncIteration:
                    # self.trace(3, 'catched StopAsyncIteration')
                    # Always empty the buffered events
                    if len(processors):
                        self.logger.info(f'received StopAsyncIteration, running pipeline processors in end mode: pipeline="{self.name}"')
                        # self.trace(4, f'running processors in end mode')
                        async for _event in self._run_commands(commands=processors, event=None, ending=True, remain=0):
                            # self.trace(5, f'yield event from processors in end mode: {_event.signature}')
                            yield _event
                    # If the pipeline runs in infinte mode, reset its iterator
                    # and yield None to indicate the end of the current loop.
                    # The iterator will be reset in the new loop.
                    if infinite:
                        self.logger.debug(f'received StopAsyncIteration, reset pipeline loop: pipeline="{self.name}"')
                        # self.trace(4, 'inifite mote, reset iterator and yield None')
                        iterator = None
                        next_event = None
                        # yield None
                    # Otherwise, simply break the pipeline loop.
                    else:
                        self.logger.debug(f'received StopAsyncIteration, breaking pipeline loop: pipeline="{self.name}"')
                        # self.trace(4, 'standard mode, return')
                        return
                # ---
                # Process the received event.
                if len(processors):
                    # self.trace(3, f'running processors on event {next_event and next_event.signature or None}')
                    # self.trace(3, f'processors: {processors}')
                    async for _event in self._run_commands(commands=processors, event=next_event, ending=False, remain=0):
                        # self.trace(4, f'yield event from processors: {_event.signature}')
                        yield _event
                    # Reinitialize next event
                    next_event = None
                elif next_event:
                    yield next_event
            #     # ---
            #     # Control state
            #     if not self._ready:
            #         self.logger.debug(f'pipeline state switched to not ready, breaking pipeline loop: pipeline="{self.name}')
            #         break
            # # ---
            # # Process buffered events
            # self.logger.debug(f'terminating pipeline: pipeline="{self.name}"')
            # # self.ending = True
            # if len(processors):
            #     self.logger.info(f'running pipeline processors in end mode: pipeline="{self.name}"')
            #     async for _event in self._run_commands(commands=processors, event=None, ending=True, remain=0):
            #         yield _event
        # ---
        # Done
        # self.logger.debug(f'finished pipeline: pipeline="{self.name}"')
        # # If we're in an infinite pipeline, yield None to indicate
        # # that the loop has been ran.
        # if infinite:
        #     yield None
        # # If we're in a finite pipeline, simply return.
        # else:
        #     return


class InfiniteRunner:

    def __init__(self, pipeline, context, event):
        """
        :param pipeline:    Pipeline instance (already initialized)
        :param context:     Pipeline context
        :param event:       Pipeline source event
        """
        # Run the pipeline in infinite mode; this will not yield
        # any event but properly init the pipeline loop.
        self.pipeline = pipeline(context, event, infinite=True)

    async def setup(self):
        await self.pipeline.__anext__()

    async def __call__(self, event):
        try:
            next_event = await self.pipeline.asend(event)
            while next_event:
                yield next_event
                next_event = await self.pipeline.asend(None)
            return
        except StopAsyncIteration:
            yield
