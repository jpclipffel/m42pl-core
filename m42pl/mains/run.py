import os
import json

import m42pl
from m42pl.event import Event
from m42pl.utils.errors import CLIErrorRender

from .__base__ import RunAction


class Run(RunAction):
    """Run a M42PL script.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('run', *args, **kwargs)
        # Required - Source file
        self.parser.add_argument('source', type=str, help='M42PL script')

    def __call__(self, args):
        super().__call__(args)
        with open(args.source, 'r') as fd:
            try:
                source = fd.read()
                context = m42pl.command('script')(source=source)()
                dispatcher = m42pl.dispatcher(args.dispatcher)(
                    context=context,
                    workdir=os.path.dirname(args.source)
                )
                dispatcher(Event(data=args.event and json.loads(args.event) or {}))
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise
