import signal
import regex
import sys
import os
from pathlib import Path
from textwrap import dedent
import getpass

# import requests

from pygments.lexer import RegexLexer
from pygments import token
from pygments.styles import get_style_by_name

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import HTML
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls

import m42pl
from m42pl.event import Event
from m42pl.utils.errors import CLIErrorRender
from m42pl.utils.text import str_to_bool

from .__base__ import RunAction


class M42PLLexer(RegexLexer):
    """M42PL grammar lexer.
    """
    name = 'M42PL'
    aliases = ['m42pl', 'mpl']
    filenames = ['*.m42pl', '*.mpl']
    tokens = {
        'root': [
            (r'(^|\|)\s*[a-zA-Z_]+[a-zA-Z_0-9\.-]*', token.Name.Function),
            (r'\'', token.Literal.String, 'string_squotes'),
            (r'\"', token.Literal.String, 'string_dquotes'),
            (r'\{', token.Name.Entity, 'jsonpath'),
            (r'[0-9]+(\.[0-9]+)?', token.Literal.Number),
            (r'\s+(as|with|to|from)\s+', token.Keyword.Pseudo),
            (r'(=|\s+)(yes|Yes|YES|true|True|TRUE|no|No|NO|false|False|FALSE)', token.Keyword.Constant)
        ],
        'string_squotes': [
            (r'[^\']+', token.Literal.String),
            (r'\'', token.Literal.String, '#pop')
        ],
        'string_dquotes': [
            (r'[^\"]+', token.Literal.String),
            (r'\"', token.Literal.String, '#pop')
        ],
        'jsonpath': [
            (r'[^\}]+', token.Name.Entity),
            (r'\}', token.Name.Entity, '#pop')
        ]
    }


class REPLCompleter(Completer):
    """REPL prompt custom completer.
    """

    rex_command = regex.compile(r'^(?P<command>[a-zA-Z_]+[a-zA-Z_-]*)(\s*)(?P<arguments>.*)')

    def __init__(self, builtins: list[str] = []):
        """
        :param builtins: List of builtins commands
        :ivar rex: Regex to match command being typed
        """
        super().__init__()
        self.builtins = builtins

    def get_completions(self, document, complete_event):
        # Build list of commands
        commands = [i for i, _ in m42pl.commands.ALIASES.items()] + self.builtins
        # Focus on command being typed
        line = ''.join(filter(None, document.text[0:document.cursor_position].split('|')[-1])).strip()
        # Extract command segments
        matched = regex.match(self.rex_command, line)
        # Process
        if matched:
            # Autocomplete command name
            # TODO: Autocomplete command arguments
            if len(matched.group('command')) > 0 and len(matched.group('arguments')) == 0:
                for command_name in commands:
                    if command_name.startswith(matched.group('command')):
                        yield Completion(command_name, start_position=-1*(len(matched.group('command'))))


class PromptPrefix:
    """Prompt prefix for M42PL REPL.
    """

    def __init__(self, prefix: str = 'm42pl'):
        self.prefix = prefix + ' | '

    def builtins(self):
        return {
            'u': getpass.getuser(),
            'w': os.getcwd()
        }

    def __call__(self):
        return HTML(self.prefix.format_map(self.builtins()))


class Builtins:
    """Handles M42PL REPL builtins.
    """

    def __init__(self, repl):
        """
        :param repl: REPL2 instance
        """
        self.repl = repl
        self.server_url = None
        # self.session = requests.Session()

    def list_builtins(self) -> list[str]:
        """
        Returns the list of builtins commands.
        """
        return [
            k.split('builtin_')[1]
            for k
            in dir(self) if k.startswith('builtin_')
        ]

    def __call__(self, source: str):
        """Tries to run ``source`` as a builtin or fails.
        """
        command, *arguments = source.split(' ')
        builtin = f'builtin_{command}'
        try:
            return getattr(self, builtin)(*arguments)
        except AttributeError:
            return source
        except Exception as error:
            raise error

    def builtin_help(self, *args):
        """Display this help.
        """
        for name in self.list_builtins():
            doc = next(iter(getattr(self, f'builtin_{name}').__doc__.splitlines()), '').rstrip('.')
            print(dedent(f'''\
                {name}
                {doc}
            '''))

    def builtin_exit(self, *args):
        """Exits the REPL.
        """
        sys.exit(0)

    def builtin_modules(self, *args):
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

    def builtin_import(self, name: str):
        """Import a M42PL module.
        """
        m42pl.load_module_name(name)

    def builtin_reload(self, *args):
        """Reload imported modules.
        """
        m42pl.reload_modules()
        self.repl.dispatcher = None

    def builtin_cd(self, path: str = '~'):
        """Change working directory.
        """
        if path is None:
            print('Usage: cd <path>')
        else:
            os.chdir(str(Path(path).expanduser().absolute()))

    def builtin_pwd(self, *args):
        """Print the current working directory.
        """
        print(os.getcwd())

    def builtin_ml(self, state: str = None):
        """Switch multiline input on/off.
        """
        # Set multiline mode
        if isinstance(state, str):
            if state in ['yes', 'true', 'on']:
                self.repl.prompt.multiline = True
                self.repl.prompt.bottom_toolbar = self.repl.prompt_bottom_toolbar
            elif state in ['no', 'false', 'off']:
                self.repl.prompt.multiline = False
                self.repl.prompt.bottom_toolbar = None
            else:
                print('Usage: ml {yes|no|true|false|on|off}')
        # Switch mutliline edit mode
        else:
            self.repl.prompt.multiline = not self.repl.prompt.multiline
        # Info
        print(f"Multiline {self.repl.prompt.multiline and 'enabled' or 'disabled'}")
        if self.repl.prompt.multiline:
            print('Type <Esc> <Enter> to execute')
    
    def builtin_plan(self, state: str = ''):
        """Run pipelines in plan mode.
        """
        self.repl.plan_only = str_to_bool(state, default=not self.repl.plan_only)
        print(f'Plan mode is {self.repl.plan_only and "enabled" or "disabled"}')

    def builtin_planout(self, state: str = ''):
        """Dump pipeline plan after execution.
        """
        self.repl.plan_output = str_to_bool(state, default=not self.repl.plan_output)
        print(f'Plan output is {self.repl.plan_output and "enabled" or "disabled"}')


class REPL2(RunAction):
    """A REPL to run M42PL pipelines.

    Pipelines are run with the ``local_repl`` dispatcher.
    This dispatcher will add an ``output`` command at the end of the
    pipeline if not already present.

    :ivar dispatcher_alias: Default dispatcher to use
    :ivar history_file: Readline history file path
    """

    dispatcher_alias = 'local_repl'
    history_file = Path(os.environ.get('HOME'), '.m42pl_history') # type: ignore

    prompt_keys_bindings = KeyBindings()

    # @staticmethod
    def prompt_bottom_toolbar(self):
        """Prompt Toolkit's bottom toolbar.
        """
        if self.prompt.multiline is True:
            return 'Run: <Esc> <enter>'

    @staticmethod
    def prompt_continuation(width, line_number, is_soft_wrap):
        """Prompt Toolkit's prompt continuation.
        """
        return ' ' * width

    @prompt_keys_bindings.add('c-c')
    def _(event):
        event.current_buffer.transform_current_line(lambda _: '')

    def __init__(self, *args, **kwargs):
        super().__init__('repl', *args, **kwargs)
        # Optional - History file
        self.parser.add_argument('-H', '--history', type=str, default=None,
            help='History file')
        # Optional - Prompt prefix
        self.parser.add_argument('-p', '--prefix', type=str, default=None,
            help='Prompt prefix')
        # Void the dispatcher instance
        self.dispatcher = None
        # Builtins
        self.builtins = Builtins(self)
        # Plan mode
        self.plan_only = False
        self.plan_output = False

    def stop(self, sig = None, frame = None):
        sys.exit(-1)

    def __call__(self, args):
        super().__call__(args)
        # Setup PromptToolkit
        self.prompt = PromptSession(
            PromptPrefix(args.prefix or '<bold>m42pl@{w}</bold>'),
            multiline=True,
            bottom_toolbar=self.prompt_bottom_toolbar,
            prompt_continuation=self.prompt_continuation,
            history=FileHistory(args.history or self.history_file),
            completer=REPLCompleter(builtins=self.builtins.list_builtins()),
            lexer=PygmentsLexer(M42PLLexer),
            style=style_from_pygments_cls(get_style_by_name('one-dark')),
            include_default_pygments_style=False,
            key_bindings=self.prompt_keys_bindings
        )
        # Select and connect KVStore
        kvstore = m42pl.kvstore(args.kvstore)(**args.kvstore_kwargs)
        # REPL loop
        while True:
            try:
                # Register SINGINT (note the underlying pipelines will also
                # register it; thats why we need regsiter it after each loop)
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                # Read and cleanup script
                source = self.prompt.prompt().strip()
                # Process
                if len(source) > 0:
                    # Run builtins
                    source = self.builtins(source)
                    # Interpret source as a M42PL pipeline
                    if source and len(source) > 0:
                        if source[0] != '|':
                            source = f'| {source}'
                        if not self.dispatcher:
                            self.dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
                        self.dispatcher(
                            source=source,
                            kvstore=kvstore,
                            event=Event(args.event),
                            plan=self.plan_only
                        )
                        # Render plan
                        if self.plan_only or self.plan_output:
                            print(self.dispatcher.plan.render())
            except EOFError:
                self.stop()
            except BlockingIOError:
                print('------\nBIOR\n------')
                pass
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise
