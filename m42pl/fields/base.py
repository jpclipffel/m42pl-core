from typing import Union


FieldName = Union[str, int, float]
FieldValue = Union[str, int, float]


class BaseField:
    """Base field solver.

    This field solver targets top-level variables and literal fields:

    * String literals: `"string"`, `'string'`
    * Number literals: `42`, `42.21`
    * Variables: `field='string'`, `field=42`

    Other field solvers should inherit from this base class, or at
    least respect its protocol.

    **About asynchronous methods**

    The fields accessors (`read`, `write` and `delete`) are coroutines.
    This is needed when manipulating some complex fields:

    * Sub-pipelines (see :class:`PipeField`)
    * Evaluated fields (TODO)
    * Remote fields (TODO: Redis ? HTTP ? etc.)

    Fields accessors also come in a synchronous fashion  (`_read`, 
    `_write` and `_delete`). These methods **should not** be
    used by default, but are necessary for basic operations such as
    event signing.

    :ivar name:     Field name.
                    If the field is a literal, this is also the field
                    value.
    :ivar default:  Default value to return is the field is not found.
                    Defaults to `None`.
    :ivar cast:     Cast function to apply to the value before
                    returning it. Returns raw value by default.
    :ivar literal:      True when the field is a literal value.
    """

    def __init__(self, name: FieldName, default = None, cast = lambda x: x):
        """
        :param name:        Field name.
                            If the field is a literal, this is also the 
                            field value.
        :param default:     Default value to return is the field is not
                            found. Defaults to `None`.
        :param cast:        Cast function to apply to the value before
                            returning it. Returns raw value by default.
        :ivar literal:      True when the field is a literal value.
        """
        self.name = name
        self.default = default
        self.cast = cast
        self.literal = True

    async def read(self, event: 'Event', pipeline: 'Pipeline' = None):
        """Returns (get) the configured field :attr:`self.name` from
        the given :param:`event`.

        :param event:       Event to read from.
        :param pipeline:    Current pipeline instance.
                            Default to `None`.
        """
        return self.cast(self.name)

    async def write(self, event: 'Event', value: FieldValue):
        """Writes (set) the given :param:`value` in the given :param:`data`.

        :param event:    Event to write to.
        """
        event.data[self.name] = value
        return event
    
    async def delete(self, event: 'Event'):
        """Deletes (pop) the configured :attr:`self.nane` from  the given :param:`data`.
        
        :param event:    Event to delete from.
        """
        event.data.pop(self.name, None)
        return event
