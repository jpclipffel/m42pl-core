from __future__ import annotations

import uuid
# import xxhash


# Events are the fundamental unit of information procuded and shared by M42PL
# commands. They are simple `dict` instances with three root fields:
#
# * `data`: stores the event's fields, accessible to users
# * `meta`: stores the internal-only fields, not accessible to users
# * `sign`: stores the event hash, read-only for the users


def Event(data: dict = {}, meta: dict = {}, sign = None):
    """Event factory.

    :param data: Event data
    :param meta: Event meta
    :param sign: Event signature
    """
    return {
        'data': data,
        'meta': meta,
        'sign': sign
    }


def signature(event: dict):
    """Returns an event's signature.

    If the event is not signed, sign it first then return the new
    signature.
    """
    if event.get('sign', None) is None:
        event['sign'] = str(uuid.uuid4())
        # event['sign'] = xxhash.xxh32_hexdigest(str(id(event)))
    return event['sign']


def derive(event: dict, data: dict = {}, meta: dict = {}, sign = None):
    """Copies an event.
    """
    return {
        'data': {**event['data'], **data},
        'meta': {**event['meta'], **meta},
        'sign': sign
    }
