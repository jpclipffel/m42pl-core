import jsonpath_ng

from .base import BaseField, FieldValue


class JsonField(BaseField):
    '''JSON path field solver.

    This field solver targets JSONPath fields: `{path[*].to.var}`

    Simple path expression are handled by :class:`DictField`.
    '''

    def __init__(self, *args, **kwargs):
        '''
        :ivar matcher:  Pre-compiled JSONPath expression.
        '''
        super().__init__(*args, **kwargs)
        self.matcher = jsonpath_ng.parse(self.name)
    
    def _read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        if event:
            return [ match.value for match in self.matcher.find(event.data) ]
        return self.default
    
    async def read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        return self._read(event, pipeline)
    
    def _write(self, event: 'Event', value: FieldValue):
        for match in self.matcher.find(event.data):
            match.full_path.update(value)
        return event
    
    async def write(self, event: 'Event', value: FieldValue):
        return self._write(event, value)
    
    def _delete(self, event: 'Event'):
        self.matcher.filter(lambda _: True, event.data)
        return event
    
    async def delete(self, event: 'Event'):
        return self._delete(event)
