import logging
import regex

from typing import Any

import m42pl.commands


# KVStores aliases map
ALIASES = dict() # type: Dict[str, object]

# Module-level logger
logger = logging.getLogger("m42pl.kvstores")


class KVStore:
    _aliases_ = []

    @classmethod
    def from_dict(cls: type, data: dict) -> 'KVStore':
        """Returns a new :class:`KVStore` from a :class:`dict`.
        
        The source map :param:`data` must match with the following map:

            {
                'args': [],     # KVStore's arguments list
                'kwargs': []    # KVStore's keyword arguments map
            }
        
        :param data:    :class:`dict` instance.
        """
        return object.__new__(cls).__init__(
            *data.get('args', []), 
            **data.get('kwargs', {})
        )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        module = f'{cls.__module__}.{cls.__name__}'
        # Register kvstore aliases
        for alias in cls._aliases_:
            # Asserts kvstore alias format
            if len(list(filter(None, regex.split(r'[a-zA-Z0-9_]+[a-zA-Z0-9_-]*', str(alias))))):
                raise Exception(f'invalid command alias: alias="{alias}", module_path="{module}"')
            # Register kvstore alias
            logger.info(f'registering kvstore alias: kvstore="{cls.__name__}", alias="{alias}"')
            ALIASES[alias] = cls

    def __init__(self):
        pass

    def read(self, key: str, pipeline: str = None) -> list:
        """Read a key from the KV Store.

        :param key:         Key name.
        :param pipeline:    Pipeline ID / Name.
        """
        return []
    
    def write(self, key: str, value: Any, pipeline: str = None) -> None:
        """Write (create or update) a key to the KV Store.

        :param key:         Key name.
        :param value:       Key value.
        :param pipeline:    Pipeline ID / Name.
        """
        pass

    def delete(self, key: str, pipeline: str = None) -> None:
        """Delete a key from the KV Store.

        :param key:         Key name.
        :param pipeline:    Pipeline ID / Name.
        """
        pass


class LocalKVStore(KVStore):
    _aliases_ = ['local',]

    def __init__(self):
        super().__init__()
        # Default map for keys without pipeline
        self.default = {}
        # Map for keys within pipeline
        self.pipelines = {}
    
    def read(self, key: str, pipeline: str = None) -> list:
        if pipeline:
            return self.pipelines.get(pipeline, {}).get(key, [])
        return self.default.get(key, [])
    
    def write(self, key: str, value: Any, pipeline: str = None) -> None:
        if pipeline:
            if not pipeline in self.pipelines:
                self.pipelines[pipeline] = {}
            self.pipelines[pipeline][key] = value
        else:
            self.default[pipeline][key] = value

    def delete(self, key: str, pipeline: str = None) -> None:
        if pipeline:
            self.pipelines.get(pipeline, {}).pop(key, None)
        else:
            self.default.pop(key, None)
