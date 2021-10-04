import json

import m42pl
from m42pl.event import Event
from m42pl.utils.errors import CLIErrorRender

from .__base__ import RunAction


class Run(RunAction):
    """Runs a M42PL script.
    """

    dispatcher_alias = 'local'

    def __init__(self, *args, **kwargs):
        super().__init__('run', *args, **kwargs)
        # Required - Source file
        self.parser.add_argument('source', type=str, help='Source script')

    def __call__(self, args):
        super().__call__(args)
        with open(args.source, 'r') as fd:
            source = fd.read()
            try:
                # Select, instanciate and run dispatcher
                m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)(
                    source=source,
                    kvstore=m42pl.kvstore(args.kvstore)(**args.kvstore_kwargs),
                    # event=len(args.event) and Event(args.event) or None
                    event=Event(args.event)
                )
            except Exception as error:
                print(CLIErrorRender(error, source).render())
                if args.raise_errors:
                    raise
