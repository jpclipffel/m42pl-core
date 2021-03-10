from copy import deepcopy
import hashlib
import time
import uuid
import sys


# from m42pl.fields import Field, BaseField


class Event:
    """A single unit of information produced and processed by commands.
    
    :attr data:         Public, JSON-serilizable fields.
    :attr meta:         Private, binary-serializable fields.
    :attr signature:    Event signature (lazy-evaluated).
    """

    __slots__ = ('data', 'meta', '_signature')

    def __init__(self, data: dict = None, meta: dict = None, signature: str = None):
        """
        :param data:        Event data.
        :param meta:        Event meta data.
        :param signature:   Event signature.
                            Defaults to `None` (lazy-evaluated).
        """
        self.data = data or {}
        self.meta = meta or {}
        self._signature = signature

    @property
    def signature(self):
        """Returns the event signature, generating it if necessary.
        """
        if not self._signature:
            self._signature = str(uuid.uuid4())
        return self._signature
    
    @signature.setter
    def signature(self, value):
        """Sets the event signature.
        """
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
        """Returns an event copy.
        """
        return Event(
            data=deepcopy(self.data, memo),
            meta=deepcopy(self.meta, memo),
            signature=self.signature
        )

    def derive(self, data: dict = {}, meta: dict = {}, signature: str = None):
        """Returns a copied and updated event.

        :param data:        Fields to add to existing data.
                            Existing data fields will be updated.
                            Defaults to an empty dict.
        :param meta:        Fields to add to existing meta.
                            Defaults to an empty dict.
                            Existing meta fields will be updated.
        :param signature:   New event signature.
                            Defaults to None (signature left empty).
        """
        # return Event(
        #     data={**deepcopy(self.data), **data},
        #     meta={**deepcopy(self.meta), **meta},
        #     signature=signature
        # )
        return Event(
            data={**self.data, **data},
            meta={**self.meta, **data},
            signature=signature
        )
