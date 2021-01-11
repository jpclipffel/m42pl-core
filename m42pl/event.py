from copy import deepcopy
import hashlib
import time
import uuid
import sys


# from m42pl.fields import Field, BaseField


class Event:
    """An M42PL event.
    
    The single unit of information produced and processed by commands.
    
    :attr data:         Public, JSON-serilizable fields.
    :attr meta:         Private, binary-serializable fields.
    :attr signature:    Event signature (lazy-evaluated).
    """

    __slots__ = ('data', 'meta', '_signature')

    def __init__(self, data: dict = {}, meta: dict = {}, signature: str = None):
        """
        :param data:        Event data.
        :param meta:        Event meta data.
        :param signature:   Event signature.
                            Defaults to `None` (lazy-evaluated).
        """
        self.data = data
        self.meta = meta
        self._signature = signature

    @property
    def signature(self):
        if not self._signature:
            self._signature = str(uuid.uuid4())
        return self._signature
    
    @signature.setter
    def signature(self, value):
        self._signature = value

    # def sign(self, fields: list = []):
    #     """Set the event signature.
        
    #     The signature of an event can change over time. It is either
    #     random, either computed using the value of the given fields.
        
    #     :param fields:  Update signature using the given fields only.
    #                     If no field is requested, the signature remains
    #                     unchanged.
    #                     FIXME: The current implementation uses field's
    #                     `_read` method (not asynchrounous) and should
    #                     be replaced by another solution.
    #     """
    #     if len(fields):
    #         if isinstance(fields[0], LiteralField):
    #             self._signature = hashlib.md5(''.join([ str(f.read_sync(self)) for f in fields ]).encode()).hexdigest()
    #         else:
    #             self._signature = hashlib.md5(''.join([ str(Field(f).read_sync(self)) for f in fields ]).encode()).hexdigest()
    #     else:
    #         self._signature = str(uuid.uuid4())
    #     return self._signature
    
    def __deepcopy__(self, memo):
        return Event(data=deepcopy(self.data, memo), meta=deepcopy(self.meta, memo), signature=self.signature)
