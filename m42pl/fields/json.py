from __future__ import annotations

import jsonpath_ng

from m42pl.pipeline import Pipeline

from .__base__ import BaseField, FieldValue
from .dict import DictField


class JsonField(BaseField):
    """JSON path field solver.

    This field solver targets JSON path fields: `{path[*].to.var}`

    **Limitations**

    * The underlying package `jsonpath_ng` does not allow to create a
      new field from an expression. Thus, if no field is found during
      a `write` operation, a new field is created using `DictField`.
      However, `DictField` solves only simple expression, and cannot
      handles complex expressions such as arrays selection.
    """

    def __init__(self, *args, **kwargs):
        """
        :ivar matcher:  Pre-compiled JSONPath expression.
        """
        super().__init__(*args, **kwargs)
        self.literal = False
        self.matcher = jsonpath_ng.parse(self.name)
    
    async def _read(self, event: dict, *args, **kwargs):
        if event:
            matched =  [
                match.value
                for match
                in self.matcher.find(event['data'])
            ]
            if len(matched):
                if len(matched) > 1:
                    return matched
                elif len(matched) == 1:
                    return matched[0]
        return self.default
    
    async def _write(self, event: dict, value: FieldValue):
        # First, attempt to match then update field.
        matched = self.matcher.find(event['data'])
        if len(matched):
            for match in matched:
                match.full_path.update(event['data'], value)
        # If no field is matched, create a new one using a `DictField`.
        # This solution does not handle complex structure such as
        # arrays.
        # TODO: Improve behaviour when adding a new field.
        else:
            event = await DictField(self.name)._write(event, value)
        # Done, return event.
        return event
    
    async def _delete(self, event: dict):
        self.matcher.filter(lambda _: True, event['data'])
        return event
