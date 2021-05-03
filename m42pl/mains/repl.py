import readline
import regex
import sys
import os
from pathlib import Path

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
    regex_builtins = regex.compile(r'^(?P<name>exit|modules)(\s.*)?$', flags=regex.IGNORECASE)

    def __init__(self, *args, **kwargs):
        super().__init__('repl', *args, **kwargs)
        # Optional - History file
        self.parser.add_argument('-H', '--history', type=str, default=None,
            help='History file')
        # Setup readline
        self.aliases = []
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer)

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
        sys.exit(0)

    def builtin_modules(self):
        print(f'{os.linesep}Imported modules')
        for name, module in m42pl.modules.items():
            print(f'* {name}: {module}')
        print(f'{os.linesep}Modules imported by name')
        for name in m42pl.IMPORTED_MODULES_NAMES:
            print(f'* {name}')
        print(f'{os.linesep}Modules imported by path')
        for name in m42pl.IMPORTED_MODULES_PATHS:
            print(f'* {name}')

    def __call__(self, args):
        super().__call__(args)
        # Build aliases list for completer
        self.aliases = [
            alias for alias, _
            in m42pl.commands.ALIASES.items()
        ]
        # Select and instanciate dispatcher
        dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
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
                # Read and cleanup script
                source = input(self.prompt).lstrip(' ').rstrip(' ')
                if len(source):
                    # Try to interpret source as builtin
                    rx = self.regex_builtins.match(source)
                    if rx:
                        getattr(self, f'builtin_{rx.groupdict()["name"]}')()

                    # # Built-in command: exit
                    # if regex.match(r'^exit(\s.*)?$', source, flags=regex.IGNORECASE):
                    #     break
                    # # Build-int command: reload
                    # if regex.match(r'^reload(\s.*)?$', source, flags=regex.IGNORECASE):
                    #     print(f'reloaded: {", ".join(m42pl.reload_modules())}')
                    # # Built-in command: help
                    # elif regex.match(r'^help(\s.*)?$', source, flags=regex.IGNORECASE):
                    #     print('No help yet')

                    # Otherwise, interpret source as a M42PL pipeline
                    else:
                        readline.write_history_file(self.history_file)
                        dispatcher(source, kvstore, Event(args.event))
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise
