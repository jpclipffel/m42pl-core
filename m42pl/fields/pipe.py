from __future__ import annotations
from traceback import print_tb

from m42pl.pipeline import Pipeline, InfiniteRunner
from m42pl.context import Context

from .__base__ import BaseField, FieldValue


class PipeField(BaseField):
    """M42PL sub-pipeline field solver.

    This field solver targets M42PL pipelines:

        | command [ | foo | bar | ... ]

    The type of the returned value depends on the sub pipeline result:

    * If the sub pipeline produces a single event with a single field,
      then only this field's value is returned.
    * If the sub pipeline produces more than one event or at least one
      event with more than one field, all events are returned as a list.
    * Otherwise, the default value is returned.

    :ivar name: Pipeline reference in current context
                (minus the leading '@').
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.literal = False
        self.results = []
        self.runner = None

    async def _read(self, event: dict, pipeline: Pipeline|None = None, context: Context|None = None):
        # Initialize pipeline runner
        if self.runner is None:
            self.runner = InfiniteRunner(
                context.pipelines[self.name],
                context,
                event
            )
            await self.runner.setup()
        # Run pipeline and collect results
        results = []
        async for _event in self.runner(event):
            results.append(_event)
        # Format and return the result
        # At least one event:
        if len(results):
            # Single event:
            if len(results) == 1:
                # Single event && single field:
                if len(results[0].get('data', {})) == 1:
                    return list(results[0].get('data', {}).items())[0][1]
                # Single event && multiple fields
                return results[0].get('data', {})
            # Multiple events
            return [result.get('data', {}) for result in results]
        # No event at all:
        return self.default
