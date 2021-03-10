from typing import Union, Optional, Collection


# pylint: disable=unsubscriptable-object
FieldName   = Union[str, int, float]
FieldValue  = Union[str, int, float]
FieldType   = Union[type, Collection[type], None]


class BaseField:
    """Base field solver.

    Other field solvers should inherit from this base class and respect
    its API.

    **About fields solvers inheritance**

    Each field solver **should** implements the following methods:

    * `_read`: Read (solves) the field value
    * `_write`: Write (set, update) the field value
    * `_delete`: Delete the field

    If a field solver does not implement a method (e.g. `_write`), an
    exception will be raised if the solver method is called during the
    pipeline execution. For instance, the `PipeField` solver (which
    solves value by running a sub-pipeline) does not permit to write a
    field to a sub-pipeline.

    **About asynchronous methods**

    The fields accessors (`read`, `write` and `delete`) are coroutines.
    This is needed when manipulating some complex fields:

    * Sub-pipelines (see :class:`PipeField`)
    * Evaluated fields (see :class:`EvalField`)
    * Remote fields (TODO: Redis ? HTTP ? etc.)

    :ivar name:     Field name.
                    If the field is a literal, this is also the field
                    value.
    :ivar default:  Default value to return is the field is not found.
                    Defaults to `None`.
    :ivar cast:     Cast function to apply to the value before
                    returning it. Returns raw value by default.
    :ivar literal:  True when the field is a literal value.
    """

    def __init__(self, name: FieldName, default = None,
                    type: FieldType = None,
                    seqn: bool = False):
        """
        :param name:        Field name.
                            If the field is a literal, this is also the 
                            field value.
        :param default:     Default value to return is the field is not
                            found. Defaults to `None`.
        :param type:        Accepted fields type(s). If a list is
                            returned, each item is tested.
                            Default to `None` (no type check).
        :param seqn:        Always returns a list of values.
                            If a command accepts a multiple values for
                            a field, this should be set to `True` to
                            ensure a list is always returned.
                            Default to `False`.
                        
        :ivar literal:      True when the field is a literal value.
        :ivar allow_seqn:   True if a sequence (list, tuple, set) is an
                            accepted type.
        """
        self.name = name
        self.default = default
        self.type = type
        self.seqn = seqn
        # ---
        self.literal = True

    async def _read(self, event, pipeline):
        """Gets the configured field.

        This method should be implemented by a child class.
        """
        raise NotImplementedError()

    async def read(self, event: 'Event', pipeline: 'Pipeline' = None):
        """Fetches, normalizes and returns the configured field.

        :param event:       Event to read from.
        :param pipeline:    Current pipeline instance.
                            Default to `None`.
        """

        def enlist(value):
            if not isinstance(value, (list, tuple, set)) and self.seqn:
                return [value, ]
            return value

        def check(items):
            for item in isinstance(items, (list, tuple, set)) and items or [items, ]:
                if self.type and not isinstance(item, self.type):
                    raise Exception(f'Invalid type for field {self.name}')
            return items

        return enlist(check(await self._read(event, pipeline)))

    async def _write(self, event, value: FieldValue):
        """Sets the configured field.

        This method should be implemented by a child class.
        """
        raise NotImplementedError()

    async def write(self, event: 'Event', value: FieldValue):
        """Sets the configured field.

        :param event:   Event to write to.
        :param value:   Value to set.
        """
        return await self._write(event, value)
    
    async def _delete(self, event):
        """Removes the configured field.

        This method should be implemented by a child class.
        """
        raise NotImplementedError()

    async def delete(self, event: 'Event'):
        """Removes the configured field.

        :param event:   Event to delete from.
        """
        return await self._delete(event)
