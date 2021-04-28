import asyncio
from types import SimpleNamespace
from collections import OrderedDict

from ..errors import FieldInitError

from .literal import LiteralField
from .json import JsonField
from .dict import DictField
from .seqn import SeqnField
from .pipe import PipeField
from .eval import EvalField
from .none import NoneField


def Field(name, *args, **kwargs):
    """Fields factory function.

    :param name:    The field name or literal value
    """

    try:
        # List or tuple
        if isinstance(name, (list, tuple)):
            return SeqnField([Field(f) for f in name])
        # Number
        elif isinstance(name, (bool, int, float)):
            return LiteralField(name, *args, **kwargs)
        # String and string sub-types
        elif isinstance(name, str):
            # Boolean
            if name in ['yes', 'true']:
                return LiteralField(True, *args, **kwargs)
            elif name in ['no', 'false']:
                return LiteralField(False, *args, **kwargs)
            # Literal
            elif name[0] == '\'' and name[-1] == '\'':
                return LiteralField(name[1:-1], *args, **kwargs)
            # Json path
            elif name[0] == '{' and name[-1] == '}':
                return JsonField(name[1:-1])
            # Eval field
            elif name[0] == '`' and name[-1] == '`':
                return EvalField(name[1:-1])
            # Pipeline reference
            elif name[0] == '@':
                return PipeField(name[1:], *args, **kwargs)
            # Dict key with space
            elif name[0] == '"' and name[-1] == '"':
                return DictField(name[1:-1], *args, **kwargs)
            # Dict key without space
            else:
                return DictField(name, *args, **kwargs) # type: ignore
        # Invalid or empty field
        else:
            return NoneField(name) # type: ignore
    # Field creation error
    except Exception as error:
        raise FieldInitError(name, str(error))


class FieldsMap:
    """Access multiples fields within a single container.
    """

    def __init__(self, **fields):
        self.fields = OrderedDict(fields)

    async def read(self, event, pipeline) -> SimpleNamespace:
        return SimpleNamespace(**type({})([
            (name, field)
            for name, field
            in zip(
                self.fields.keys(),
                await asyncio.gather(*[
                    field.read(event, pipeline) for _, field in self.fields.items()
                ])
            )
        ]))
