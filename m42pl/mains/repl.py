import readline
import signal
import regex
import sys
import os
from pathlib import Path
from textwrap import dedent

import m42pl
from m42pl.event import Event
from m42pl.utils.errors import CLIErrorRender

from .__base__ import RunAction


class REPL(RunAction):
    """A basic REPL to run M42PL pipelines.

    Pipelines are run with the `local_shell` dispatcher.
    This dispatcher will add an `output` command at the end of the
    pipeline if not already present.

    :ivar prompt:       Input prompt
    :ivar history_file: Readline history file path
    :ivar aliases:      Commands aliases list (used by readline for
                        autocompletion)
    """

    dispatcher_alias = 'local_repl'
    prompt = 'm42pl | '
    history_file = Path(os.environ.get('HOME'), '.m42pl_history') # type: ignore

    # Builtins command regex
    regex_builtins = regex.compile(
        r'^(?P<name>exit|modules|reload|help)(\s.*)?$',
        flags=regex.IGNORECASE
    )

    def __init__(self, *args, **kwargs):
        super().__init__('repl', *args, **kwargs)
        # Optional - History file
        self.parser.add_argument('-H', '--history', type=str, default=None,
            help='History file')
        # Setup readline
        self.aliases = []
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer)
        # Initialize the dispatcher instance
        self.dispatcher = None

    def completer(self, text, state):
        """Readline completer.

        :param text:    Input text
        :param state:   Matching state
        """
        matched = [
            alias for alias
            in self.aliases
            if alias.startswith(text)
        ] + [None,]
        return matched[state]

    def builtin_exit(self):
        """Exits the REPL.
        """
        sys.exit(0)

    def builtin_modules(self):
        """Prints the imported modules.
        """
        print(f'{os.linesep}Imported modules')
        for name, module in m42pl.modules.items():
            print(f'* {name}: {module}')
        print(f'{os.linesep}Modules imported by name')
        for name in m42pl.IMPORTED_MODULES_NAMES:
            print(f'* {name}')
        print(f'{os.linesep}Modules imported by path')
        for name in m42pl.IMPORTED_MODULES_PATHS:
            print(f'* {name}')
    
    def builtin_reload(self):
        """Reload imported modules.
        """
        m42pl.reload_modules()
        self.dispatcher = None

    def builtin_help(self):
        """Display a help message.
        """
        print(dedent('''\
            Welcome to M42PL !

            Builtins commands:
            * exit      : Quit the interpreter
            * modules   : Print the list of imported modules
            * reload    : Reload the imported modules
            * help      : Display this help message

            Snippets:
            * Type 'exit' or Ctrl+D to leave the interpreter
            * Type 'commands' to generate the list of commands
            * Type 'command <command name>' to show a command help
        '''))

    def stop(self, sig = None, frame = None):
        sys.exit(-1)

    def __call__(self, args):
        super().__call__(args)
        # Build aliases list for completer
        self.aliases = [
            alias for alias, _
            in m42pl.commands.ALIASES.items()
        ]
        # Select and instanciate dispatcher
        # dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
        # Select and connect KVStore
        kvstore = m42pl.kvstore(args.kvstore)(**args.kvstore_kwargs)
        # Read history file
        if args.history:
            self.history_file = Path(args.history)
        if self.history_file.is_file():
            readline.read_history_file(self.history_file)
        # Print status
        print(f'{len(self.aliases)} commands loaded')
        # REPL loop
        while True:
            try:
                # Register SINGINT (note the underlying pipelines will also
                # register it; thats why we need regsiter it after each loop)
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                # Read and cleanup script
                source = input(self.prompt).lstrip(' ').rstrip(' ')
                if len(source):
                    # Try to interpret source as builtin
                    rx = self.regex_builtins.match(source)
                    if rx:
                        getattr(self, f'builtin_{rx.groupdict()["name"]}')()
                    # Otherwise, interpret source as a M42PL pipeline
                    else:
                        if not self.dispatcher:
                            self.dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
                        readline.write_history_file(self.history_file)
                        self.dispatcher(
                            source=source,
                            kvstore=kvstore,
                            # event=len(args.event) > 0 and Event(data=args.event) or None
                            event=Event(args.event)
                        )
            except EOFError:
                self.stop()
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise
