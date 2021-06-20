from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline

from m42pl.errors import CommandError

from .__base__ import AsyncCommand


class MetaCommand(AsyncCommand):
    """Controls the events pipeline.
    """

    async def __call__(self, event: dict, pipeline: Pipeline,
                        *args, **kwargs) -> AsyncGenerator[dict, None]:
        """Runs the command.
        
        Always yields the received event.
        
        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        try:
            await self.target(event, pipeline)
        except Exception as error:
            raise CommandError(command=self, message=str(error)) from error
        yield event

    async def target(self, event: dict, pipeline: Pipeline) -> None:
        """MetaCommand target method.

        Always yields the received event.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        pass
