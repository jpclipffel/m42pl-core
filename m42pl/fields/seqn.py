from .__base__ import BaseField, FieldValue


class SeqnField(BaseField):

    async def _read(self, *args, **kwargs):
        return [ await i.read(*args, **kwargs) for i in self.name ]
