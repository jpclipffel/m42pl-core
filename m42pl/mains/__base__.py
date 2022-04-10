import os
from pathlib import Path
import json

import m42pl


class Action:
    """Base command line action.

    **DO NOT INHERIT FROM THIS CLASS** when implementing an action.
    Use one of the child class :class:`DebugAction` or
    :class:`RunAction`.

    :ivar log_levels:   List of valid log levels
    :ivar parser:       Argparse parser instance
    """

    log_levels = ['debug', 'info', 'warning', 'error', 'critical']

    def __init__(self, name: str, subparser):
        self.parser = subparser.add_parser(name)
        self.parser.set_defaults(func=self)
        # Log level
        self.parser.add_argument('-l', '--log-level', type=str.lower,
            default='warning', choices=self.log_levels, help='Log level')
        # Extra modules
        self.parser.add_argument('-m', '--module', action='append',
            default=[], help='External module name (may be specified multiple times)')

    def __call__(self, args):
        """Runs the command line action.

        Each command (i.e. child class of `Action`) **should** call
        their parent's :meth:`__call__`, e.g.:

        .. code-block:: Python

            def __call__(self, args):
                super().__call__(args)

        :param args:    Command arguments
        """
        # Load modules
        m42pl.find_modules(args.module)


class DebugAction(Action):
    """Base command line action to debug/test/hack M42PL.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # # Log level
        # self.parser.add_argument('-l', '--log-level', type=str.lower,
        #     default='warning', choices=self.log_levels, help='Log level')
        # # Extra modules
        # self.parser.add_argument('-m', '--module', action='append',
        #     default=[], help='External module name (may be specified multiple times)')
    
    def __call__(self, args):
        super().__call__(args)


class RunAction(Action):
    """Base command line action to run M42PL scripts.

    :ivar dispatcher_alias: Dispacther alias (name)
    """

    dispatcher_alias = 'local_repl'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional - Dispatcher
        self.parser.add_argument('-d', '--dispatcher', type=str,
            default=self.dispatcher_alias, help='Dispatcher name')
        # Optional - Dispatcher kwargs
        self.parser.add_argument('-D', '--dispatcher-kwargs', type=str,
            default='{}', help='Dispatcher keyword arguments as JSON string')
        # Optional - KVStore
        self.parser.add_argument('-k', '--kvstore', type=str,
            default='local', help='KVStore name')
        # Optional - KVStore kwargs
        self.parser.add_argument('-K', '--kvstore-kwargs', type=str,
            default='{}', help='KVStore keyword arguments as JSON string')
        # Optional - Initial event data as a JSON string
        self.parser.add_argument('-e', '--event', type=str,
            default='{}', help='Initial event (JSON)')
        # Debug - Raise errors
        self.parser.add_argument('-r', '--raise-errors', dest='raise_errors',
            action='store_true', default=False, help='Raise errors')
    
    def __call__(self, args):
        super().__call__(args)
        # Parse initial event
        args.event = json.loads(args.event)
        # Parses dispatcher and kvstore kwargs
        args.dispatcher_kwargs = json.loads(args.dispatcher_kwargs)
        args.kvstore_kwargs = json.loads(args.kvstore_kwargs)
