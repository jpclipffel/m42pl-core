from m42pl.context import Context
import re
import sys
import logging

import m42pl
import m42pl.commands
from m42pl.event import Event
from m42pl.kvstores import KVStore


# Dispatchers aliases map
ALIASES = dict() # type: dict[str, object]

# Module-level logger
logger = logging.getLogger("m42pl.dispatchers")


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

    :ivar _aliases_:  List of dispatcher names.
    """

    _aliases_ = []

    @staticmethod
    def flatten_commands(commands: list) -> list:
        """Separates commands tuples, i.e. commands whom `__new__`
        returned more than one object.
        
        :param commands:    Commands list.
        """
        _commands = []
        for command in commands:
            if type(command) in [ tuple, list ]:
                _commands += Dispatcher.flatten_commands(command)
            else:
                _commands.append(command)
        return _commands
    
    @staticmethod
    def split_commands(commands) -> list:
        _commands = [] # type: list
        _subcommands = [] # type: list
        for command in commands:
            if isinstance(command, m42pl.commands.MergingCommand):
                _commands.append(_subcommands)
                _commands.append([command, ])
                _subcommands = []
            else:
                _subcommands.append(command)
        _commands.append(_subcommands)
        return _commands

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
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

    def target(self, context: Context, event: Event):
        """Runs the dispatcher.

        This method must be implemented by the actual dispatcher class,
        and should:

        * Enters KVStore context (e.g. `with context.kvstore: ...`)
        * Handle execution and pipeline exceptions 

        :param context: Pipelines context
        :param event:   Initial event
        """
        pass

    def __call__(self, source: str, kvstore: KVStore, event: Event = None):
        """Prepares to runs the dispatcher.

        :param source:  Script source
        :param kvstore: KVStore instance
        :param event:   Initial event
        """
        return self.target(
            context = Context(
                pipelines=self.script(source)(),
                kvstore=kvstore
            ),
            event=event or Event()
        )
