from .__base__ import BaseField


class NoneField(BaseField):
    """Dummy field solver class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _read(self, *args, **kwargs):
        return None

    async def _write(self, *args, **kwargs):
        return None

    async def _delete(self, *args, **kwargs):
        return None
