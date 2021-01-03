from ..errors import FieldInitError

from .base import BaseField, FieldName
from .json import JsonField
from .dict import DictField
from .seqn import SeqnField
from .pipe import PipeField
from .eval import EvalField
from .none import NoneField


def Field(name: FieldName, *args, **kwargs):
    '''Fields factory function.

    The correct field implementation is choosen this way:

    ```
        ├── list, tuple
        │   └── SeqnField
        ├── bool, int, float
        │   └── BaseField
        ├── str
        │   ├── Literal string
        │   |   └── BaseField
        │   ├── JSONPath
        │   |   └── JsonField
        │   ├── Pipeline reference
        │   |   └── PipeField
        │   ├── Other string
        │       └── DictField
        └── other
            └── NoneField
    ```

    :param name:    The field name or literal value.
    '''

    try:
        # ---
        # List or tuple
        if type(name) in [list, tuple]:
            # print(f'field({name}) -> {type(name)} -> ListField')
            return SeqnField([ Field(f, *args, **kwargs) for f in name ])
        # ---
        # Number
        elif type(name) in [bool, int, float]:
            # print(f'field({name}) -> {type(name)} -> BaseField')
            return BaseField(name, *args, **kwargs)
        # ---
        # String and string sub-types
        elif isinstance(name, str):
            # ---
            # Literal
            if name[0] in ['\'', '"'] and name[-1] in ['\'', '"']:
                # print(f'field.field({name}) -> string -> BaseField')
                name = name[1:-1]
                return BaseField(name, *args, **kwargs)
            # ---
            # Json path
            elif name[0] == '{' and name[-1] == '}':
                # print(f'field({name}) -> string -> JsonField ({name})')
                return JsonField(name[1:-1])
            # ---
            # Eval field
            elif name[0] == '`' and name[-1] == '`':
                return EvalField(name[1:-1])
            # ---
            # Pipeline reference
            elif name[0] == '@':
                # print(f'field({name}) -> string -> PipeField ({name})')
                return PipeField(name[1:], *args, **kwargs)
            # ---
            # Dict key
            else:
                # print(f'field({name}) -> string -> DictField')
                return DictField(name, *args, **kwargs) # type: ignore
        # ---
        # Invalid or empty field
        else:
            # print(f'field({name}) -> None ({type(name)}) -> NoneField')
            return NoneField(name) # type: ignore
    # ---
    # Field creation error
    except Exception as error:
        raise FieldInitError(name, str(error))
