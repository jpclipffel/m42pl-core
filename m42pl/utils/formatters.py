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
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, event: Event):
        return str(event.data)


class Json(Formatter):
    """Formats event as a JSON string.
    """

    class JSONDecoder(json.JSONEncoder):
        """JSON decoder for :class:`Event`.
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
        def default(self, o):
            return repr(o)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dumper = partial(
            json.dumps,
            *args, 
            **{
                **kwargs,
                **{'cls': self.JSONDecoder}
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
