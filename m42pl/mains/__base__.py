import m42pl


class Action:
    """Base command line action.
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

        ```
        def __call__(self, args):
            super().__call__(args)
        ```

        :param args:    Command arguments.
        """
        m42pl.load_modules(names=args.module)


class DebugAction(Action):
    """Base command line action to debug/test/hack M42PL.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, args):
        super().__call__(args)


class RunAction(Action):
    """Base command line action to run M42PL scripts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional - Generator timeout
        self.parser.add_argument('-t', '--timeout', type=float, default=0.0,
            help='Pipelines timeout')
        # Optional - Select dispatcher
        self.parser.add_argument('-d', '--dispatcher', type=str,
            default='local', help='Pipeline dispatcher name')
        # # Optional - Initial event data as a JSON stirng
        self.parser.add_argument('-e', '--event', type=str,
            default=None, help='Initial event data')
        # Debug - Raise errors
        self.parser.add_argument('-r', '--raise-errors', dest='raise_errors',
            action='store_true', default=False, help='Raise errors')
    
    def __call__(self, args):
        super().__call__(args)
