from .base import BaseField


class NoneField(BaseField):
    '''Dummy field solver class.
    '''

    def _read(self, *args, **kwargs):
        return None

    async def read(self, *args, **kwargs):
        return None

    def _write(self, *args, **kwargs):
        return None

    async def write(self, *args, **kwargs):
        return None

    def _delete(self, *args, **kwargs):
        return None

    async def delete(self, *args, **kwargs):
        return None
