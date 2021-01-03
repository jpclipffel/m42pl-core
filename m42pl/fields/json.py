import jsonpath_ng

from .base import BaseField, FieldValue
from .dict import DictField


class JsonField(BaseField):
    """JSON path field solver.

    This field solver targets JSON path fields: `{path[*].to.var}`

    **Limitations**

    * The underlying package `jsonpath_ng` does not allow to create a
      new field from an expression. Thus, if no field is found during
      a `write` operation, a new field is created using `DictField`.
    * As `DictField` solves only simple expression, it cannot handles
      complex expressions such as arrays selection.
    """

    def __init__(self, *args, **kwargs):
        """
        :ivar matcher:  Pre-compiled JSONPath expression.
        """
        super().__init__(*args, **kwargs)
        self.literal = False
        self.matcher = jsonpath_ng.parse(self.name)
    
    def _read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        if event:
            matched =  [ match.value for match in self.matcher.find(event.data) ]
            return len(matched) > 1 and matched or matched[0]
        return self.default
    
    async def read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        return self._read(event, pipeline)
    
    def _write(self, event: 'Event', value: FieldValue):
        # First, attempt to match then update fields.
        matched = self.matcher.find(event.data)
        if len(matched):
            for match in matched:
                match.full_path.update(event.data, value)
        # If no field is matched, create a new one using a `DictField`.
        # This solution does not handle complex structure such as
        # arrays.
        # TODO: Improve behaviour when adding a new field.
        else:
            event = DictField(self.name)._write(event, value)
        # Done, return event.
        return event
    
    async def write(self, event: 'Event', value: FieldValue):
        return self._write(event, value)
    
    def _delete(self, event: 'Event'):
        self.matcher.filter(lambda _: True, event.data)
        return event
    
    async def delete(self, event: 'Event'):
        return self._delete(event)
