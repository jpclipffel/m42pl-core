from .__base__ import BaseField, FieldValue


class DictField(BaseField):
    """Variables and nest variables field solver.

    This field solver targets variables-like fields:

    * Variable name: `foo`
    * Variable path: `foo.bar.baz`, `foo.a-long_name.baz`
    """

    def __init__(self, *args, **kwargs):
        """
        :ivar path:     Field path as list.
        """
        super().__init__(*args, **kwargs)
        self.literal = False
        self.path = list(filter(None, self.name.split('.')))
    
    async def _read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
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

    async def _write(self, event: 'Event', value: FieldValue):
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

    async def _delete(self, event: 'Event'):
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
