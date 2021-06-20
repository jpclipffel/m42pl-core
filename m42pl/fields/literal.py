from __future__ import annotations

from m42pl.pipeline import Pipeline

from .__base__ import BaseField, FieldValue


class LiteralField(BaseField):
    """Literal fields solver.
    
    This field solver targets literal fields:

    * String literals: `"string"`, `'string'`
    * Number literals: `42`, `42.21`
    * Variables: `field='string'`, `field=42`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.literal = True

    async def _read(self, event: dict, pipeline: Pipeline|None = None):
        """Returns (get) the configured field :attr:`self.name` from
        the given :param:`event`.

        :param event:       Event to read from.
        :param pipeline:    Current pipeline instance.
                            Default to `None`.
        """
        return self.name

    async def _write(self, event: dict, value: FieldValue):
        """Writes (set) the given :param:`value` in the given :param:`data`.

        :param event:    Event to write to.
        """
        event['data'][self.name] = value
        return event
    
    async def _delete(self, event: dict):
        """Deletes (pop) the configured :attr:`self.nane` from  the given :param:`data`.
        
        :param event:    Event to delete from.
        """
        event['data'].pop(self.name, None)
        return event
