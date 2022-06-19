from __future__ import annotations

from m42pl.pipeline import Pipeline
from m42pl.utils.eval import Evaluator

from .__base__ import BaseField, FieldValue


class EvalField(BaseField):
    """Evaluation field solver.

    This field solver targets eval expression.
    """

    def __init__(self, *args, **kwargs):
        """
        :ivar expr:     Expression evaluator
        """
        super().__init__(*args, **kwargs)
        expr = self.name.replace('\n', ' ').strip(' ')
        self.expr = Evaluator(expr)

    async def _read(self, event: dict, *args, **kwargs):
        try:
            return self.expr(event and event.get('data', {}) or {})
        except Exception:
            return self.default
