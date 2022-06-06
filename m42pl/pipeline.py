from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Union

if TYPE_CHECKING:
    from m42pl.context import Context

import logging
from contextlib import AsyncExitStack
import asyncio
import signal

import m42pl
from m42pl import errors
from m42pl.event import Event
from m42pl.utils.log import LoggerAdapter
from m42pl.commands import (
    MetaCommand,
    GeneratingCommand,
    StreamingCommand,
    BufferingCommand
)


# Any command type
AnyCommmand = Union[
    MetaCommand,
    GeneratingCommand,
    StreamingCommand,
    BufferingCommand
]


class Pipeline:
    """Holds a list of commands.

    :ivar logger: Logger instance
    :ivar metas: Leading meta commands
    :ivar generator: Generating command
    :ivar processors: Processing commands
    """

    @classmethod
    def from_dict(cls, data: dict) -> object:
        """Returns a new :class:`Pipeline` from a :class:`dict`.

        The source map ``data`` must match with the following map:

        .. code-block:: python

            {
                'commands': [               # Commands list
                    {
                        'alias': '...',     # Name (alias)
                        'args': [],         # Arguments
                        'kwargs': {}        # Keyword arguments
                    },
                ],
                'subrefs': []               # Sub-pipelines references
            }

        **Important**: This function does not invoke the commands'
        `__new__` method: this means that :param:`data` must have been
        generated from an already built pipeline, i.e. whoms commands
        have been instanciated.
        The underlying reason is that commands may overload their
        `__new__` method to return more than one class instance.
        
        :param data: Source pipeline as :class:`dict`
        """
        # Build the commands list
        commands = []
        for command in data['commands']:
            commands.append(object.__new__(m42pl.command(command['alias'])))
            commands[-1].__init__(*command.get('args', []), **command.get('kwargs', {}))
        # Remove original commands list from dict
        data.pop('commands')
        # Builds and returns a new pipeline
        return cls(commands=commands, subrefs=data['subrefs'])

    @staticmethod
    def flatten_commands(commands) -> Generator:
        """Flatten the commands list.

        This is necessary as some commands ``__new__`` may returns more
        than one class instance.

        :param commands: Commands list
        """
        for command in commands:
            if isinstance(command, (tuple, list)):
                yield from Pipeline.flatten_commands(command)
            else:
                yield command

    def __init__(self, commands: list = [], name: str = 'main',
                    subrefs: list = []) -> None:
        """
        :param commands: Commands list
        :param name: Pipeline name
        :param subrefs: Sub-piplines references
        """
        self.commands = commands
        self.name = name
        self.subrefs = subrefs
        self.logger = LoggerAdapter(
            defaults={'pipeline_name': name},
            logger=logging.getLogger('m42pl.pipeline')
        )
        # Build
        self.build()
        # Pipeline state
        self._commands_set = False
        self._ready = True

    def to_dict(self) -> dict:
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
            ],
            'subrefs': self.subrefs
        }

    def build(self) -> None:
        """(Re)builds the pipeline.

        Building the pipeline means:
        * Ensuring there is at most one (1) generating command
        * Differenciating generating, meta and processing commands

        This method should be called each time the pipeline commands
        list is modified.
        """
        self.logger.info(f'building pipeline: pipeline="{self.name}"')
        # ---
        # Initialize commands sets
        self.metas: list[AnyCommmand] = []
        self.generator: GeneratingCommand|None = None
        self.processors: list[AnyCommmand] = []
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
                self.processors.append(command)
        # Rewrite commands list
        self.commands = list(filter(None, self.metas + [self.generator,] + self.processors))

    def set_chunk(self, chunk: int = 0, chunks: int = 1) -> None:
        """Set the pipeline's commands chunk number and chunks count.

        :param chunk: Current chunk number (starts at ``0``)
        :param chunks: Total chunks count (minimum is ``1``)
        """
        for command in self.commands:
            command.chunk = (chunk, chunks)


class PipelineRunner:
    """Runs a pipeline.

    :ivar pipeline: Pipeline instance
    :ivar tracing: ``True`` if execution is traced, ``False`` otherwise
    :ivar logger: Logger instance
    :ivar _ready: ``True`` if the runner is ready, ``False`` otherwise
    :ivar _commands_set: ``True`` if the ``pipeline`` commands have
        been set, ``False`` otherwise
    """

    def __init__(self, pipeline: Pipeline, tracing: bool = False) -> None:
        """
        :param pipeline: Pipeline instance
        :param tracing: ``True`` to enable tracing, ``False`` otherwise
        """
        self.pipeline = pipeline
        self.tracing = tracing
        self.logger = LoggerAdapter(
            defaults={'pipeline_name': pipeline.name},
            logger=logging.getLogger('m42pl.pipeline.PipelineRunner')
        )
        self._ready = True
        self._commands_set = False

    def trace(self, level: int, message: str) -> None:
        """Traces (print...) a pipeline state.

        :param level: Current depth
        :param message: Message to print
        """
        if self.tracing:
            print(f'{"." * level * 2} {self.pipeline.name}: {message}')

    def stop(self, *args, **kwargs) -> None:
        """Stops the pipeline.
        """
        self.logger.warning('forcefully stopping the pipeline')
        self._ready = False
        raise StopAsyncIteration('SINGINT')

    async def setup_commands(self, event: dict|None) -> None:
        """Setups the commands list (commands post-initialization).

        Some commands' internals (e.g. fields) may requires access to
        the pipeline (and nested objects such as context or parents
        and children pipelines) to finish their initialization.

        Once set, the commands are **not** set again even if this
        method is called more than once.

        :param event: Last received event (may be ``None``).
        """
        if not self._commands_set:
            self.logger.debug(f'setting-up pipeline commands')
            for command in self.pipeline.commands:
                # Override command logger
                command.logger = LoggerAdapter(
                    {'pipeline_name': self.pipeline.name},
                    logging.getLogger(f'm42pl.commands.{command.__module__}.{command.__class__.__name__}')
                )
                # Setup command
                try:
                    await command.setup(event=event, pipeline=self.pipeline, context=self.context)
                except Exception as error:
                    if not isinstance(error, errors.M42PLError):
                        raise errors.CommandError(command, message=str(error))
                    else:
                        raise error
            # Do not re-setup commands (needed for sub pipelines)
            self._commands_set = True
        else:
            self.logger.debug(f'pipeline commands already set')

    async def run_commands(self, commands, event, ending, remain):
        """Runs a commands list.

        :param commands: Commands list
        :param event: Current event
        :param ending: ``True`` if the pipeline is ending, ``False``
            otherwise
        :param remain: Amount or remaining events in the previous
            command
        """
        if len(commands):
            # Current command instance and children commands
            command, has_further_commands = commands[0], len(commands) > 1
            # Run command and children commands
            try:
                async for _event in command(
                        event=event,
                        pipeline=self.pipeline,
                        context=self.context,
                        ending=ending,
                        remain=remain
                    ):
                    if has_further_commands:
                        async for __event in self.run_commands(
                                commands[1:],
                                _event,
                                ending,
                                (remain + await command.remain())
                            ):
                            yield __event
                    elif _event:
                        yield _event
                # else:
                #     print(f'run commands > for else')
                #     if ending:
                #         print('run commands > for else > ending')
                #         if has_further_commands:
                #             print('run commands > for else > has further commands')
                #             async for _event in self.run_commands(commands[1:], None, ending, remain):
                #                 yield _event
                #         elif event:
                #             print('run commands > for else > yield event')
                #             yield event
            # Command errors handling
            except errors.CommandError as error:
                print(error.name, error.line, error.column, error.offset)
                print(str(error))
                print()

    async def __call__(self, context: Context|None = None,
                        event: dict|None = None, infinite: bool = False,
                        timeout: float = 0.0):
        """Runs the pipeline.

        :param context: Current context
        :param event: Initial event
        :param infinite: ``True`` if the pipeline should run forever,
            ``False`` otherwise
        :param timeout: Generator timeout to force pipeline wakeup
        """
        # Setup context
        self.context = context
        # Setup signal handler
        signal.signal(signal.SIGINT, self.stop)
        # ---
        # Setup commands
        await self.setup_commands(event or Event())
        # ---
        # Enter pipeline context
        async with AsyncExitStack() as stack:
            self.logger.debug(f'entering commands contexts')
            # Enter commands context
            metas = [
                await stack.enter_async_context(cmd)
                for cmd in self.pipeline.metas
            ]
            generator = self.pipeline.generator and \
                await stack.enter_async_context(self.pipeline.generator) \
                or None
            processors = [
                await stack.enter_async_context(cmd)
                for cmd in self.pipeline.processors
            ]
            # Run pipeline metas
            self.logger.info(f'running pipeline metas')
            async for _ in self.run_commands(metas, event, False, 0):
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
                iterator = generator and generator(
                    event=event,
                    pipeline=self.pipeline,
                    context=self.context
                ).__aiter__() or None
            # ---
            # Start pipeline loop
            next_event = event
            # while self._ready:
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
                        # self.trace(3, f'initial event: {next_event and next_event["sign"] or None}')
                        if next_event:
                            # self.trace(4, f'initial event is not None, reset iterator on it')
                            iterator = generator and generator(
                                event=next_event,
                                pipeline=self.pipeline,
                                context=self.context
                            ).__aiter__() or None
                        # else:
                            # self.trace(4, f'initial event is None, pipeline should raise StopAsyncIteration right after')
                    # ---
                    # If the pipeline has a generating command derived into an
                    # iterator, it retrieves its next event from this iterator.
                    if iterator:
                        # self.trace(3, f'iterator is set, await next event')
                        if timeout > 0.0:
                            task = asyncio.create_task(iterator.__anext__())
                            # self.trace(4, f'task shiedled: {task}')
                            next_event = await asyncio.wait_for(
                                asyncio.shield(task),
                                timeout)
                        else:
                            next_event = await iterator.__anext__()
                    # ---
                    # If neither the calling function nor the generator had 
                    # yield an event, stop the iteration.
                    if next_event is None:
                        self.logger.info(f'next_event is None, breaking')
                        # self.trace(3, f'next event is None, raise StopAsyncIteration')
                        raise StopAsyncIteration()
                # ---
                # Timeout occurs when the iterator took too long to yield an
                # event. Send None to the processors to 'wake-up' the
                # buffering commands and process the buffered events.
                except asyncio.TimeoutError:
                    self.logger.debug(f'generator timeout, forcing pipeline wakeup')
                    # self.trace(4, f'shielded task {task} -> wake up !')
                    async for e in self.run_commands(processors, None, False, 0):
                        yield e
                    next_event = await task # type: ignore
                # ---
                # StopAsyncIteration occurs when either the iterator or the
                # calling function have finished to produce events.
                except StopAsyncIteration:
                    # self.trace(3, 'catched StopAsyncIteration')
                    # Always empty the buffered events
                    if len(processors):
                        self.logger.info(f'received StopAsyncIteration, running pipeline processors in end mode')
                        # self.trace(4, f'running processors in end mode')
                        async for _event in self.run_commands(processors, None, True, 0):
                            # self.trace(5, f'yield event from processors in end mode: {_event.signature}')
                            yield _event
                    # If the pipeline runs in infinte mode, reset its iterator
                    # and yield None to indicate the end of the current loop.
                    # The iterator will be reset in the new loop.
                    if infinite:
                        self.logger.debug(f'received StopAsyncIteration, reset pipeline loop')
                        # self.trace(4, 'inifite mote, reset iterator and yield None')
                        iterator = None
                        next_event = None
                    # Otherwise, simply break the pipeline loop.
                    else:
                        self.logger.debug(f'received StopAsyncIteration, breaking pipeline loop')
                        # self.trace(4, 'standard mode, return')
                        return
                # ---
                # Process the received event.
                if len(processors):
                    # self.trace(3, f'running processors on event {next_event and next_event["sign"] or None}')
                    # self.trace(3, f'processors: {processors}')
                    async for _event in self.run_commands(processors, next_event, False, 0):
                        # self.trace(4, f'yield event from processors: {_event["sign"]}')
                        yield _event
                    # Reinitialize next event
                    next_event = None
                elif next_event:
                    yield next_event


class InfiniteRunner:
    """Runs a pipeline forever.

    This runner ensure the pipeline will continue to run even after
    reaching the last event. This is usefull when the pipeline does not
    need to be (re)initialized, e.g. when used as a sub-pipeline.

    :ivar iter: Pipeline iterator
    """

    def __init__(self, pipeline, context, event):
        """
        :param pipeline: Pipeline instance (already initialized)
        :param context: Pipeline context
        :param event: Pipeline source event
        """
        # Run the pipeline in infinite mode; this will not yield
        # any event but properly init the pipeline loop.
        self.iter = PipelineRunner(pipeline)(context, event, infinite=True)

    async def setup(self):
        await self.iter.__anext__()

    async def __call__(self, event):
        try:
            next_event = await self.iter.asend(event)
            while next_event:
                yield next_event
                next_event = await self.iter.asend(None)
            return
        except StopAsyncIteration:
            yield
