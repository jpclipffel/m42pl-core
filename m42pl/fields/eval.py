from m42pl.utils.eval import Evaluator

from .__base__ import BaseField, FieldValue


class EvalField(BaseField):
    """Evaluation field solver.

    This field solver targets eval expression.
    """

    def __init__(self, *args, **kwargs):
        """
        :ivar expr:     Expression evaluator.
        """
        super().__init__(*args, **kwargs)
        self.expr = Evaluator(self.name)
        
    async def _read(self, event: 'Event' = None, pipeline: 'Pipeline' = None):
        try:
            return self.expr(event and event.data or {})
        except Exception:
            return self.default
