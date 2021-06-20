from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import logging
import regex

from m42pl.errors import EncodingError, DecodingError


# Formatters aliases map
ALIASES = dict() # type: dict[str, object]

# Module-level logger
logger = logging.getLogger('m42pl.encoders')

# Encoder field type
Data = Union[dict, str, int, float, list, bytes]


class Encoder:
    """Base data encoder class.

    Encoders can encode and decode an event or an event's field 
    to / from a given format, such as JSON, MessagePack, BSON, etc.

    As for :class:`m42pl.Command`, the :class:`Formater`s are
    implemented  as plugins modules:

    * They are loaded by `m42pl.load_modules()` (or 
      `m42pl.load_module_name()` or `m42pl.load_module_path()`)
    * They are *registered* in `m42pl.formatters.ALIASES` 
      (map bettwen a encoder's aliases and its class)
    * They are requested through `m42pl.encoder()`

    To implement an encoder, one should create a class inheriting 
    from this base class (:class:`m42pl.encoders.Encoder`).
    This base class is responsible for the encoder's *registration*
    (:meth:`__init_subclass__`).

    :ivar _aliases_:  List of encoder names.
    """

    _aliases_: list[str] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs) # type: ignore
        module = f'{cls.__module__}.{cls.__name__}'
        # Register encoder aliases
        for alias in cls._aliases_:
            # Asserts encoder alias format
            if len(list(filter(None, regex.split(r'[a-zA-Z0-9_]+[a-zA-Z0-9_-]*', str(alias))))):
                raise Exception(f'invalid encoder alias: alias="{alias}", module_path="{module}"')
            # Register encoder alias
            logger.info(f'registering encoder alias: encoder="{cls.__name__}", alias="{alias}"')
            ALIASES[alias] = cls

    def __init__(self, *args, **kwargs):
        """
        :param args:        Args list to be automatically
                            exported using `to_dict()`
        :param kwargs:      Kwargs map to be automatically
                            exported using `to_dict()`
        
        :ivar logger:       Encoder instance logger
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def _encode(self, data: Data) -> bytes|str:
        return bytes()

    def encode(self, data: dict) -> bytes|str:
        """Encodes :param:`data`.

        This method wraps the encoder's `_encode()`:

        * Validate data type to encode
        * Raise proper exception if an error occurs

        :param data:    Data to encode
        """
        try:
            if not isinstance(data, dict):
                raise EncodingError(
                    encoder=self,
                    message=(
                        f'Invalid data type: expected {type(dict)}, '
                        f'got {type(data)}'
                    )
                )
            return self._encode(data)
        except EncodingError:
            raise
        except Exception as error:
            raise EncodingError(self, str(error)) from error
    
    def _decode(self, data: bytes|str) -> Data:
        return {}

    def decode(self, data: bytes|str) -> dict:
        """Decodes :param:`data`.

        This method wraps the encoder's `_encode()`:

        * Validate data type to decode
        * Raise proper exception if an error occurs

        :param data:    Data to decode
        """
        def filter_dict(decoded) -> dict:
            if not isinstance(decoded, dict):
                raise DecodingError(
                    encoder=self,
                    message=(
                        f'Invalid data type: expected {type(dict)}, '
                        f'got {type(data)}'
                    )
                )
            return decoded

        try:
            return filter_dict(self._decode(data))
        except DecodingError:
            raise
        except Exception as error:
            raise DecodingError(self, str(error)) from error
