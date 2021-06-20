from m42pl.pipeline import Pipeline

from .__base__ import BaseField, FieldValue


class SeqnField(BaseField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _read(self, *args, **kwargs):
        values = [
            (await field.read(*args, **kwargs))
            for field
            in self.name
        ]
        if len(values):
            return values
        return self.default
