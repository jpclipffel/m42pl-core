import m42pl

from .__base__ import DebugAction


class Grammar(DebugAction):
    """Prints a command grammar.
    """

    def __init__(self, *args, **kwargs):
        super().__init__('grammar', *args, **kwargs)
        self.parser.add_argument('command', type=str, help='Command name')
    
    def __call__(self, args):
        super().__call__(args)
        print(m42pl.command(args.command)._ebnf_)
