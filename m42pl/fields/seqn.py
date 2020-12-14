from .base import BaseField, FieldValue


class SeqnField(BaseField):

    def _read(self, *args, **kwargs):
        return [ i._read(*args, **kwargs) for i in self.name ]

    async def read(self, *args, **kwargs):
        return [ await i.read(*args, **kwargs) for i in self.name ]
