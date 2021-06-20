from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline

from m42pl.errors import CommandError

from .__base__ import AsyncCommand


class StreamingCommand(AsyncCommand):
    """Receives, process and yields events.
    """

    async def __call__(self, event: dict, pipeline: Pipeline,
                        *args, **kwargs) -> AsyncGenerator[dict, None]:
        """Runs the command.
        
        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        if event:
            try:
                async for _event in self.target(event, pipeline):
                    yield _event
            except Exception as error:
                raise CommandError(command=self, message=str(error)) from error
        else:
            yield event

    async def target(self, event: dict,
                        pipeline: Pipeline) -> AsyncGenerator[dict, None]:
        """Process and yields events.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        yield event
