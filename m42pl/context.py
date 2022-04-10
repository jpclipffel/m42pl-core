from collections import OrderedDict

import m42pl
import m42pl.pipeline
from .kvstores import KVStore


class Context:
    """Contains a script's pipelines, variables, etc.
    """
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Context':
        """Returns a new :class:`Context` from a :class:`dict`.
        """
        return cls(
            pipelines=dict([
                (name, m42pl.pipeline.Pipeline.from_dict(pipeline))
                for name, pipeline
                in data['pipelines'].items()
            ]),
            kvstore=m42pl.kvstore(data['kvstore']['alias'])(
                *data['kvstore']['args'],
                data['kvstore']['kwargs']
            )
        )

    def __init__(self, pipelines: dict, kvstore: KVStore):
        """
        :param pipelines: Pipelines dict (name:instance)
        :param kvstore: KVStore instance
        """
        self.pipelines = pipelines
        self.kvstore = kvstore

    def to_dict(self):
        """Serializes the context as a :class:`dict`.
        """
        return {
            'pipelines': dict([(name, pipeline.to_dict()) for name, pipeline in self.pipelines.items()]),
            'kvstore': self.kvstore.to_dict()
        }

    def add_pipelines(self, pipelines: dict):
        """Add one or more pipelines to the context.

        :param pipelines: Pipelines to add to the context
        """
        self.pipelines.update(pipelines)
