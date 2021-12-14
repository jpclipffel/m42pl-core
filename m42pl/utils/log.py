from __future__ import annotations

import logging
import json


class LoggerAdapter(logging.LoggerAdapter):
    """A generic logger adapter for M42PL components.
    """

    def __init__(self, defaults: dict, logger, extra={}):
        super().__init__(logger, extra)
        self.defaults = defaults

    def process(self, msg, kwargs):
        return (
            f'{msg}: {json.dumps({**self.defaults, **kwargs})}',
            {}
        )

    def getChild(self, *args, **kwargs):
        return self.logger.getChild(*args, **kwargs)
