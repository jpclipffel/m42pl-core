from copy import deepcopy
from inspect import signature
import uuid


class Event:
    """A single unit of information produced and processed by commands.
    
    :attr data:         Public, JSON-serilizable fields
    :attr meta:         Private fields
    :attr signature:    Event signature (property, lazy-evaluated)
    """

    __slots__ = ('data', 'meta', '_signature')

    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Returns a new :class:`Event` from a :class:`dict`.

        :param data:    Event serialized as a :class:`dict`
        """
        return cls(
            data=data.get('data', None),
            meta=data.get('meta', None),
            signature=data.get(signature, None)
        )

    def __init__(self, data: dict = None, meta: dict = None,
                    signature: str = None):
        """
        :param data:        Event data.
        :param meta:        Event meta data.
        :param signature:   Event signature.
                            Defaults to `None` (lazy-evaluated).
        """
        self.data = data or {}
        self.meta = meta or {}
        self._signature = signature

    def to_dict(self) -> dict:
        """Serializes the event as a :class:`dict`.
        """
        return {
            'data': self.data,
            'meta': self.meta,
            'signature': self.signature
        }

    @property
    def signature(self) -> str:
        """Returns the event signature.

        If the event is not yet signed, a new signature is computed and
        returned.
        """
        if not self._signature:
            self._signature = str(uuid.uuid4())
        return self._signature
    
    @signature.setter
    def signature(self, value: str) -> None:
        """Sets the event signature.

        :param value:   Signature
        """
        self._signature = value

    def __deepcopy__(self, memo) -> 'Event':
        """Returns an event copy.

        :param memo:    Deepcopy's memo :class:`dict`.
        """
        return Event(
            data=deepcopy(self.data, memo),
            meta=deepcopy(self.meta, memo),
            signature=self.signature
        )

    def derive(self, data: dict = {}, meta: dict = {},
                signature: str = None) -> 'Event':
        """Returns a copied and updated event.

        :param data:        Fields to add to existing data
                            Existing data fields are updated
        :param meta:        Fields to add to existing meta
                            Existing meta fields are updated
        :param signature:   New event signature
                            Defaults to `None` (signature left empty)
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
