import json
from functools import partial
# pylint: disable=no-name-in-module
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from m42pl.event import Event


class Formatter:
    """Base event formatter.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, event: Event):
        return None


class Raw(Formatter):
    """Formats event as a string.

    One should probably **not** use this formatter, as it relies
    only on Python's `str` type (and thus on `__str__` and `__repr__`).

    TODO: Remove this formatter ?
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, event: Event):
        return str(event.data)


class Json(Formatter):
    """Formats event as a JSON string.

    This formatter implements a simple custom JSON encoder, which
    will handle non-json-serializable fields by returning a three
    fields dict instead, to inform the user about the data type,
    size (if bytes) and why its is not presented as expected.
    """

    class Encoder(json.JSONEncoder):
        """JSON encoder for :class:`Event`.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
        def default(self, o):
            if isinstance(o, (bytes)):
                return {
                    'type': 'bytes',
                    'size': len(o),
                    'info': 'Data type not suitable for Json formatter'
                }
            else:
                return {
                    'type': str(type(o)),
                    'repr': str(repr(o)),
                    'info': 'Data type not suitable for Json formatter'
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dumper = partial(
            json.dumps,
            *args, 
            **{
                **kwargs,
                **{'cls': self.Encoder}
            }
        )

    def __call__(self, event: Event):
        return self.dumper(event.data) # pylint: disable=too-many-function-args


class HJson(Json):
    """Format event as a highlighted JSON string.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lexer = JsonLexer()
        self.formatter = TerminalFormatter()

    def __call__(self, event: Event):
        return highlight(
            super().__call__(event),
            self.lexer,
            self.formatter
        )
