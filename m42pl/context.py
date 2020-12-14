from collections import OrderedDict

from . import pipeline


class Context:
    '''Contains a script's pipelines, variables, etc.
    '''
    
    @classmethod
    def from_dict(cls, dc: dict) -> 'Context':
        return cls(pipelines=[
            pipeline.Pipeline.from_dict(p) for p in dc['pipelines']
        ])

    def __init__(self, pipelines: list = []):
        '''
        :param pipelines:   List of pipelines.
        '''
        self.pipelines = OrderedDict(dict([
            (p.name, p) for p in pipelines
        ]))
    
    def add_pipelines(self, pipelines: dict):
        '''Add one or more pipelines to the context.

        :param pipelines:   Pipelines to add to the context.
        '''
        self.pipelines.update(pipelines)

    def to_dict(self) -> dict:
        """Returns a JSON-serializable :class:`dict` representation.
        """
        return {
            'pipelines': [
                p.to_dict() for _, p in self.pipelines.items()
            ]
        }
