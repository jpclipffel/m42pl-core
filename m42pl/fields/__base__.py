from __future__ import annotations

from typing import Union, Collection

from m42pl.pipeline import Pipeline
from m42pl.context import Context


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
        :param name:        Field name; If the field is a literal, 
                            this is also the field value
        :param default:     Default value to return is the field is not
                            found; Defaults to `None`
        :param type:        Accepted fields type(s); If a list is
                            returned, each item is tested; Default to 
                            `None` (no type check)
        :param seqn:        Always returns a list of values if `True`;
                            If a command accepts multiple values for
                            a field, this should be set to `True` to
                            ensure a list is always returned; Defaults
                            to `False`
                        
        :ivar literal:      `True` when the field is a literal value
        """
        self.name = name
        self.default = default
        self.type = type
        self.seqn = seqn
        self.literal = True

    async def _read(self, event: dict, pipeline: Pipeline|None = None, context: Context|None = None):
        """Gets the configured field.

        This method should be implemented by a child class.

        :param event:       dict from which the field must be read
        :param pipeline:    Current pipeline
        :param context:     Current context
        :return:            Read field value
        """
        raise NotImplementedError()

    async def read(self, event: dict, pipeline: Pipeline|None = None, context: Context|None = None):
        """Normalizes and returns the configured field's value.

        :param event:       dict from which the field must be read
        :param pipeline:    Current pipeline
        :param context:     Current context
        :return:            Read field value
        """

        def enlist(value):
            """Wraps the field's value into a list.
            """
            if not isinstance(value, (list, tuple, set)) and self.seqn:
                return [value, ]
            return value

        def check(items):
            """Checks the field's value type.
            """
            for item in isinstance(items, (list, tuple, set)) and items or [items, ]:
                if self.type and not isinstance(item, self.type):
                    raise Exception(f'Invalid type for field {self.name}')
            return items

        if self.name is not None:
            return enlist(check(await self._read(event, pipeline)))
        elif self.seqn:
            return []
        return None

    async def _write(self, event: dict, value: FieldValue) -> dict:
        """Sets the configured field.

        This method should be implemented by a child class.

        :param event:   dict to which the file must be write
        :param value:   Field value
        :return:        Updated event
        """
        raise NotImplementedError()

    async def write(self, event: dict, value: FieldValue) -> dict:
        """Sets the configured field.

        :param event:   dict to which the file must be write
        :param value:   Field value
        :return:        Updated event
        """
        return await self._write(event, value)
    
    async def _delete(self, event: dict) -> dict:
        """Removes the configured field.

        This method should be implemented by a child class.

        :param event:   dict from which the field must be removed
        :return:        Updated event
        """
        raise NotImplementedError()

    async def delete(self, event: dict) -> dict:
        """Removes the configured field.

        :param event:   dict from which the field must be removed
        :return:        Updated event
        """
        return await self._delete(event)
