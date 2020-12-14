from .base import BaseField, FieldValue


class DictField(BaseField):
    '''Dict-path (doted path) field solver.

    This field solver targets variables-like fields:

    * Variable name: `foo`
    * Variable path: `foo.bar.baz`

    Complex JSON path expression are handled by :class:`JsonField`.
    '''

    def __init__(self, *args, **kwargs):
        '''
        :ivar path: Field path as list (easier to navigate).
        '''
        super().__init__(*args, **kwargs)
        self.path = list(filter(None, self.name.split('.')))
    
    def _read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        if event:
            if len(self.path) == 1:
                return event.data.get(self.path[0], self.default)
            else:
                _dc = event.data
                try:
                    for _name in self.path[0:-1]:
                        _dc = _dc[_name]
                    return _dc[self.path[-1]]
                except KeyError:
                    return self.default
        else:
            return self.default
    
    async def read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        return self._read(event, pipeline)

    def _write(self, event: 'Event', value: FieldValue):
        if len(self.path) == 1:
            event.data[self.path[0]] = value
        else:
            _dc = event.data
            for _name in self.path[0:-1]:
                if _name not in _dc or not isinstance(_dc[_name], dict):
                    _dc[_name] = {}
                _dc = _dc[_name]
            _dc[self.path[-1]] = value
        return event
    
    async def write(self, event: 'Event', value: FieldValue):
        return self._write(event, value)

    def _delete(self, event: 'Event'):
        if len(self.path) == 1:
            event.data.pop(self.path[0], None)
        else:
            _dc = event.data
            for _name in self.path[0:-1]:
                if _name in _dc:
                    _dc = _dc[_name]
                else:
                    return event
            _dc.pop(self.path[-1], None)
        return event

    async def delete(self, event: 'Event'):
        return self._delete(event)
