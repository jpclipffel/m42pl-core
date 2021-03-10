import readline
import regex

import m42pl
from m42pl.utils.errors import CLIErrorRender

from .__base__ import RunAction


class REPL(RunAction):
    """A basic REPL to run M42PL pipelines.

    Pipelines are run with the `local_shell` dispatcher.
    This dispatcher will add an `output` command at the end of the
    pipeline if not already present.

    :ivar prompt:   Input prompt.
    :ivar aliases:  List of commands aliases.
    """

    prompt = 'm42pl | '

    def __init__(self, *args, **kwargs):
        super().__init__('repl', *args, **kwargs)
        # Setup readline
        self.aliases = []
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer)

    def completer(self, text, state):
        """Readline completer.
        """
        matched = [
            alias for alias
            in self.aliases
            if alias.startswith(text)
        ] + [None,]
        return matched[state]

    def __call__(self, args):
        super().__call__(args)
        # Build aliases list for completer
        self.aliases = [
            alias for alias, _
            in m42pl.commands.ALIASES.items()
        ]
        # Select M42PL script command and dispatcher instance
        script = m42pl.command('script')
        dispatcher = m42pl.dispatcher('local_repl')
        # Print status
        print(f'{len(self.aliases)} commands loaded')
        # REPL loop
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
