from __future__ import annotations

from m42pl.pipeline import Pipeline

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

    async def _read(self, event: dict, pipeline: Pipeline|None = None):
        if not pipeline:
            return self.default
        # ---
        # Select and run the sub pipeline.
        results = []
        _pipeline = pipeline and pipeline.context.pipelines.get(self.name, None) or None
        if _pipeline:
            async for _event in _pipeline(pipeline.context, event):
                results.append(_event)
        # ---
        # Format and return the result.
        #
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
