import os
import json
import asyncio
from collections import OrderedDict as odict
import tabulate

import m42pl
from m42pl.event import Event
from m42pl.utils.errors import CLIErrorRender

from .__base__ import RunAction


class Status(RunAction):
    """Get the status of a M42PL pipeline.
    """

    dispatcher_alias = 'local'

    def __init__(self, *args, **kwargs):
        super().__init__('status', *args, **kwargs)
        # Required - Pipeline / process identifier
        self.parser.add_argument('identifier', type=str, nargs='?',
            default=None, help='Pipeline identifier')
        # Optional - Output format
        self.parser.add_argument('-o', '--output', type=str,
            choices=['json', 'list'], default='list', help='Output format')

    def ouptut_json(self, items):
        for process in items:
            print(json.dumps(process, indent=2))
    
    def output_list(self, items):
        headers = ['name', 'status', 'dispatcher', 'start_time', 'end_time']
        data = []
        # ---
        for process in items:
            data.append([process.get(field, '') for field in headers])
        print(tabulate.tabulate(data, headers))

    def __call__(self, args):
        super().__call__(args)
        dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
        kvstore = m42pl.kvstore(args.kvstore)(**args.kvstore_kwargs)
        status = asyncio.run(dispatcher.status(kvstore, args.identifier))
        # ---
        if args.output == 'json':
            self.ouptut_json(status)
        elif args.output == 'list':
            self.output_list(status)
