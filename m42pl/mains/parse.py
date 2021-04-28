import m42pl
from m42pl.pipeline import Pipeline

from .__base__ import DebugAction


class Parse(DebugAction):
    """Parses a M42PL script.
    """

    # command = 'script_json'
    command = 'script'

    def __init__(self, *args, **kwargs):
        super().__init__('parse', *args, **kwargs)
        # Required - Source script
        self.parser.add_argument('source', type=str,
            help='Source script path')
    
    def __call__(self, args):
        super().__call__(args)
        with open(args.source) as fd:
            print(m42pl.command(self.command)(fd.read())())
