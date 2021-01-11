import sys
import regex
import argparse
import readline
import logging, logging.handlers
from dataclasses import dataclass

import m42pl
from m42pl.utils.time import now
from m42pl.utils.errors import CLIErrorRender
from m42pl.errors import M42PLError


# Cannot use `logging._levelNames` anymore (change from Python 3.9).
# Switch to hard-coded levels names.
LOG_LEVELS = ['debug', 'info', 'warning', 'error', 'critical']


class CLIAction:
    """Base command line action.
    """
    def __init__(self, name: str, subparser):
        self.parser = subparser.add_parser(name)
        self.parser.set_defaults(func=self)
        # Common arguments
        self.parser.add_argument('-m', '--module', action='append',
            default=[], help='External module')

    def __call__(self, args):
        """Runs the command line action.

        Each command (i.e. child class of `CLIAction`) **should** call
        their parent's :meth:`__call__`, e.g.:

        ```
        def __call__(self, args):
            super().__call__(args)
        ```

        :param args:    Command arguments.
        """
        m42pl.load_modules(names=args.module)


class Parse(CLIAction):
    """Parses a M42PL script.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('parse', *args, **kwargs)
        # Source file
        self.parser.add_argument('source', type=str, help='M42PL script')
        # Debug - Use specific parser
        self.parser.add_argument('--command', dest='command', type=str,
            default=None, help='Use the given command parser')
        # Debug - Parse mode
        self.parser.add_argument('--parse-mode', dest='mode',
            choices=['json', 'pipeline'], default='json', help='Parser mode')
        # Debug - Parse commands or not
        self.parser.add_argument('--parse-commands', dest='parse_commands',
            action='store_true', default=False, help='Parse commands')
    
    def __call__(self, args):
        super().__call__(args)
        with open(args.source) as fd:
            parsed = m42pl.command('script')(
                source=fd.read(),
                mode=args.mode, 
                parse_commands=args.parse_commands
            )()
            print(parsed)


class Grammar(CLIAction):
    """Prints a command's grammar.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('grammar', *args, **kwargs)
        self.parser.add_argument('command', help='Command name')
    
    def __call__(self, args):
        super().__call__(args)
        print(m42pl.command(args.command)._ebnf_)


class Run(CLIAction):
    """Run a M42PL script.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('run', *args, **kwargs)
        # Source file
        self.parser.add_argument('source', type=str, help='M42PL script')
        # Optional - Generator timeout
        self.parser.add_argument('-t', '--timeout', type=float, default=0.0,
            help='Pipelines timeout')
        # Optional - Select dispatcher
        self.parser.add_argument('-d', '--dispatcher', type=str,
            default='local', help='Pipeline dispatcher name / alias')
        # Debug - Raise errors
        self.parser.add_argument('-r', '--raise-errors', dest='raise_errors',
            action='store_true', default=False, help='Raise errors')

    def __call__(self, args):
        super().__call__(args)
        with open(args.source, 'r') as fd:
            try:
                source = fd.read()
                context = m42pl.command('script')(source=source)()
                dispatcher = m42pl.dispatcher(args.dispatcher)(context)
                dispatcher()
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise


class REPL(CLIAction):
    """A basic REPL to run M42PL pipelines.

    Pipelines are run with the `local_shell` dispatcher.
    This dispatcher will add an `output` command at the end of the
    pipeline if not already present.

    :ivar prompt:       Input prompt.
    :ivar aliases:      List of commands aliases.
    """

    prompt = 'm42pl | '

    def completer(self, text, state):
        """Readline completer.
        """
        matched = [
            alias for alias
            in self.aliases
            if alias.startswith(text)
        ]+ [None,]
        return matched[state]

    def __init__(self, *args, **kwargs):
        super().__init__('repl', *args, **kwargs)
        self.aliases = []
        # Setup readline
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer)

    def __call__(self, args):
        super().__call__(args)
        # Build aliases list for completer
        self.aliases = [
            alias for alias, _
            in m42pl.commands.ALIASES.items()
        ]
        # Select M42PL script command and dispatcher instance
        script = m42pl.command('script')
        dispatcher = m42pl.dispatcher('local_shell')
        # Print status
        print(f'm42pl | {len(self.aliases)} commands loaded')
        # CLI loop
        while True:
            try:
                source = input(self.prompt).lstrip(' ').rstrip(' ')
                if len(source):
                    # Built-in command: exit
                    if regex.match(r'^exit(\s.*)?$', source, flags=regex.IGNORECASE):
                        break
                    # Built-in command: help
                    elif regex.match(r'^help(\s.*)?$', source, flags=regex.IGNORECASE):
                        print('No help yet')
                    # M42PL command
                    else:
                        context = script(source)()
                        dispatcher(context)()
            except Exception as error:
                print(CLIErrorRender(error, source).render())


def main():
    # Parser instance
    parser = argparse.ArgumentParser('m42pl')
    # Common arguments
    parser.add_argument('--log-level', dest='log_level', type=str,
        default='warning', choices=LOG_LEVELS, help='Log level')
    # Sub parsers
    subparser = parser.add_subparsers(dest='command')
    subparser.required = True
    _commands = [ c(subparser) for c in [Parse, Grammar, Run, REPL] ]
    # Parse
    args = parser.parse_args()
    # Setup logging
    logger = logging.getLogger('m42pl')
    logger.setLevel(args.log_level.upper())
    handler = logging.StreamHandler()
    handler.setLevel(args.log_level.upper())
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s'))
    logger.addHandler(handler)
    # Run
    args.func(args)


if __name__ == "__main__":
    main()
