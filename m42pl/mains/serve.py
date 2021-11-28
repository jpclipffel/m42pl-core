from flask import Flask, request

import asyncio

import m42pl
from m42pl.event import Event

from .__base__ import RunAction


class Serve(RunAction):
    """Runs M42PL scripts on demand.

    This main is meant for quick tests and local deployment only.
    """

    dispatcher_alias = 'local_detached'

    def __init__(self, *args, **kwargs):
        super().__init__('serve', *args, **kwargs)

    def __call__(self, args):
        super().__call__(args)
        # Init dispatcher
        dispatcher = m42pl.dispatcher(args.dispatcher)(**args.dispatcher_kwargs)
        # Init KVStore
        kvstore = m42pl.kvstore(args.kvstore)(**args.kvstore_kwargs)
        # Init Flask app
        app = Flask('m42pl')

        @app.route('/')
        def index():
            """Returns the list of available endpoints.
            """
            return {
                'endpoints': {
                    'GET /': {
                        'description': 'Returns the list of API calls'
                    },
                    'POST /run': {
                        'description': 'Runs a pipeline',
                        'properties': {
                            'script': {
                                'description': 'M42PL script code',
                                'type': 'string'
                            },
                            'event': {
                                'description': 'Initial (source) event',
                                'type': 'object'
                            }
                        }
                    },
                    'GET /status/<pid>': {
                        'description': 'Returns the given pipeline status'
                    }
                }
            }

        @app.route('/run', methods=['POST',])
        def run():
            """Starts a new pipeline.
            """
            try:
                jsdata = request.get_json()
                script = jsdata['script']
                event  = jsdata.get('event', {})
                # ---
                pid = dispatcher(
                    source=script,
                    kvstore=kvstore,
                    event=Event(event)
                )
                # ---
                return {'pid': pid}
            except Exception as error:
                return {'error': str(error)}
                raise error
        
        @app.route('/status/<pid>')
        def status(pid: int):
            """Returns a pipeline status.
            """
            return {'status': asyncio.run(dispatcher.status_str(pid))}

        # Start Flask app
        app.run()
