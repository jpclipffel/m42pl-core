from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncGenerator, List

import logging
import regex

import m42pl.commands


# KVStores aliases map
ALIASES = dict() # type: dict[str, object]

# Module-level logger
logger = logging.getLogger('m42pl.kvstores')


class KVStore:
    """Base KVStore class.

    An M42PL KVStore provides an interface to read and write named
    keys / values pairs.
    KVStores are meant to store (relatively) static data like the
    macros code, secrets, configuration, etc.
    
    They are not meant to store dynamic data nor pipeline results.

    As for :class:`m42pl.Command`, :class:`KVStore` are implemented 
    as plugins modules:

    * They are loaded by `m42pl.load_modules()` (or 
      `m42pl.load_module_name()` or `m42pl.load_module_path()`)
    * They are *registered* in `m42pl.kvstores.ALIASES` 
      (map bettwen a KVStore's aliases and its class)
    * They are requested through `m42pl.kvstore()`

    To implement a KVStore, one should create a class inheriting 
    from this base class (:class:`m42pl.dispatchers.KVStore`).
    This base class is responsible for the KVStore's *registration*
    (:meth:`__init_subclass__`).

    :ivar _aliases_:  List of KVStores names.
    """

    _aliases_: List[str] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs) # type: ignore
        module = f'{cls.__module__}.{cls.__name__}'
        # Register kvstore aliases
        for alias in cls._aliases_:
            # Asserts kvstore alias format
            if len(list(filter(None, regex.split(r'[a-zA-Z0-9_]+[a-zA-Z0-9_-]*', str(alias))))):
                raise Exception(f'invalid kvstore alias: alias="{alias}", module_path="{module}"')
            # Register kvstore alias
            logger.info(f'registering kvstore alias: kvstore="{cls.__name__}", alias="{alias}"')
            ALIASES[alias] = cls

    @classmethod
    def from_dict(cls: type, data: dict) -> 'KVStore':
        """Returns a new :class:`KVStore` from a :class:`dict`.
        
        The source map :param:`data` must match with the following map:

            {
                'args': [],     # KVStore's arguments list
                'kwargs': {}    # KVStore's keyword arguments map
            }
        
        :param data: :class:`dict` instance.
        """
        return object.__new__(cls).__init__(
            *data.get('args', []), 
            **data.get('kwargs', {})
        )

    def __init__(self, *args, **kwargs):
        """
        :param args: Args list to be automatically exported using `to_dict()`
        :param kwargs: Kwargs map to be automatically exported using `to_dict()`
        
        :ivar logger:       Command instance logger
        :ivar _args:        Automatically exported args list
        :ivar _kwargs:      Automatically exported kwargs list
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._args, self._kwargs = args, kwargs

    def to_dict(self) -> dict:
        """Serializes the pipeline as a :class:`dict`.

        The returned :attr:`dict` must be understandable by 
        attr:`from_dict` and match with the following mapping:

            {
                'alias': ''     # KVStore's name / alias
                'args': [],     # KVStore's arguments list
                'kwargs': {}    # KVStore's keyword arguments map
            }
        """
        return {
            'alias': self._aliases_[0],
            'args': self._args,
            'kwargs': self._kwargs
        }

    async def __aenter__(self):
        """Enters KVStore context.
        """
        return self
    
    async def __aexit__(self, *args, **kwargs):
        """Exists KVStore context.
        """
        return

    async def read(self, key: str = None, default: Any = None) -> Any:
        """Reads a key from the KV Store.

        :param key:         Key name
        :param default:     Default value to return
        """
        return default
    
    async def write(self, key: str, value: Any = None) -> None:
        """Writes (create or update) a key to the KV Store.

        :param key:     Key name
        :param value:   Key value
        """
        pass

    async def delete(self, key: str = None) -> None:
        """Deletes a key from the KV Store.

        :param key:     Key name
        """
        pass

    async def items(self, key: str|None = None) -> AsyncGenerator:
        """Returns items from the KVStore.

        :param key:     Returns only items whose name starts with the
                        given key.
        """
        pass
