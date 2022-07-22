from __future__ import annotations

from m42pl.context import Context
import re
import logging
from enum import IntEnum, auto

import m42pl
import m42pl.commands
from m42pl.kvstores import KVStore
from m42pl.utils import time
from m42pl.utils.log import LoggerAdapter
from m42pl.utils.plan import Plan
from m42pl.pipeline import Pipeline
from m42pl.commands import MergingCommand


# Dispatchers aliases map
ALIASES = dict() # type: dict[str, object]

# Module-level logger
logger = logging.getLogger('m42pl.dispatchers')


class Dispatcher:
    """Base dispatcher class.

    An M42PL dispatcher is responsible for a M42PL script execution. It
    arranges to *dispatch* the script, e.g. create forks, initializes
    the remote workers, etc. and run it.

    As for :class:`m42pl.Command`, :class:`Dispatcher` are implemented 
    as plugins modules:

    * They are loaded by `m42pl.load_modules()` (or 
      `m42pl.load_module_name()` or `m42pl.load_module_path()`)
    * They are *registered* in `m42pl.dispatcher.ALIASES` 
      (map bettwen a dispatcher's aliases and its class)
    * They are requested through `m42pl.dispatcher()`

    To implement a dispatcher, one should create a class inheriting 
    from this base class (:class:`m42pl.dispatchers.Dispatcher`).
    This base class is responsible for the dispatchers's *registration*
    (:meth:`__init_subclass__`).

    :ivar _aliases_:  List of dispatcher names
    """

    _aliases_: list[str]  = []

    kvstore_prefix = 'dispatchers'

    class State(IntEnum):
        """Pipelines status, as returned by ``status()``.
        """
        UNKNOWN     = auto()
        RUNNING     = auto()
        FINISHED    = auto()
        CRASHED     = auto()

    @staticmethod
    def flatten_commands(commands: list) -> list:
        """Separates commands tuples.
        
        Commands tuples are returned by commands whoms ``__new__``
        returned more than one instance.
        
        :param commands: Commands list
        """
        _commands = []
        for command in commands:
            if type(command) in [ tuple, list ]:
                _commands += Dispatcher.flatten_commands(command)
            else:
                _commands.append(command)
        return _commands

    @staticmethod
    def split_pipeline(pipeline, unify: bool = True, max_layers: int = 2,
                        types: tuple = (MergingCommand,)) -> list:
        """Splits the given ``pipeline`` by command type.

        The source ``pipeline`` is split at each ``MergingCommand``
        and in at most ``max_layers`` layers.

        :param pipeline: Source pipeline
        :param unify: Unify merging and post-merging commands or not
        :param max_layers: Maximum number of layers; Default to 2
            (one for pre-merging commands and one for merging and
            post-merging commands)
        """
        commands = [[],]
        pipelines = []
        # Build the new pipelines' commands lists
        for cmd in pipeline.commands:
            # Split when the command type is a `MergingCommand`
            if isinstance(cmd, types) and len(commands) < max_layers:
                commands.append([cmd,])
                if not unify:
                    commands.append([])
            # Append non-merging command to current commands list
            else:
                commands[-1].append(cmd)
        # Build and returns new pipelines
        for cmds in commands:
            pipelines.append(Pipeline(
                commands=cmds,
                name=f'{pipeline.name}'
            ))
        return pipelines

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs) # type: ignore
        module = f'{cls.__module__}.{cls.__name__}'
        # Register dispatcher aliases
        for alias in cls._aliases_:
            # Asserts dispatcher alias format
            if len(list(filter(None, re.split(r'[a-zA-Z0-9_]+[a-zA-Z0-9_-]*', str(alias))))):
                raise Exception(f'invalid command alias: alias="{alias}", module_path="{module}"')
            # Register dispatcher alias
            logger.info(f'registering dispatcher alias: dispatcher="{cls.__name__}", alias="{alias}"')
            ALIASES[alias] = cls

    def __init__(self) -> None:
        self.script = m42pl.command('script')
        # self.logger = logger.getChild(self.__class__.__name__)
        self.logger = LoggerAdapter(
            defaults={},
            logger=logging.getLogger(f'm42pl.dispatcher.{self.__class__.__name__}')
        )
        # Initialize plan
        self.plan = Plan()

    def target(self, context: Context, event: dict, plan: bool = False):
        """Runs the dispatcher.

        This method must be implemented by the actual dispatcher class,
        and should:

        * Enters KVStore context (e.g. `with context.kvstore: ...`)
        * Handle execution and pipeline exceptions 

        If ``plan`` is set to ``True``, the dispatcher should not run
        the pipeline but instead return a plan, i.e. a representation
        of what would be executed.

        :param context: Pipelines context
        :param event: Initial event
        :param plan: Plan pipeline execution only
        """
        pass

    def __call__(self, source: str, kvstore: KVStore,
                    event: dict|None = None, plan: bool = False):
        """Prepares to run and runs the dispatcher.

        :param source: Script source
        :param kvstore: KVStore instance
        :param event: Initial event
        :param plan: Plan pipeline execution only
        """
        self.plan = Plan()
        return self.target(
            context = Context(
                pipelines=self.script(source)(),
                kvstore=kvstore
            ),
            event=event or dict(),
            plan=plan
        )

    async def status(self, kvstore, identifier: str|int|None) -> list:
        """Return the status of an underlying pipeline.

        :param identifier: Pipeline identifier (type is
            implementation-specific)
        """
        async with kvstore:
            if identifier is not None:
                return [await kvstore.read(
                    f'{self.kvstore_prefix}:{identifier}'),
                ]
            else:
                processes = []
                async for _, p in kvstore.items(f'{self.kvstore_prefix}:'):
                    # if p.get('dispatcher', '') == self.__class__.__name__:
                    processes.append(p)
                return processes

    async def register(self, kvstore, identifier):
        """Registers a pipeline process into a KVStore.

        :param kvstore: KVStore instance (must be ready)
        :param identifier: Pipeline process identifier
        """
        self.logger.info('registering pipeline process')
        await kvstore.write(
            f'{self.kvstore_prefix}:{identifier}',
            {
                'name': str(identifier),
                'dispatcher': self.__class__.__name__,
                'start_time': time.now().timestamp(),
                'end_time': None,
                'status': self.State.RUNNING.value
            }
        )

    async def unregister(self, kvstore, identifier):
        """Unregisters a pipeline process form a KVStore.

        :param kvstore: KVStore instance (must be ready)
        :param identifier: Pipeline process identifier
        """
        self.logger.info('unregistering pipeline process')
        await kvstore.delete(f'{self.kvstore_prefix}:{identifier}')

    async def cleanup(self, kvstore):
        """Cleanup all dead pipeline processes from a KVStore.
        """
        processes = await kvstore.read(self.kvstore_prefix, default=[])
        for process in processes:
            # if process.get('dispacther') == self.__class.__name__:
            print(process)

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args, **kwargs):
        pass
