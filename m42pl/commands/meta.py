from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline
    from m42pl.context import Context

from m42pl.errors import CommandError

from .__base__ import AsyncCommand


class MetaCommand(AsyncCommand):
    """Controls the events pipeline.
    """

    async def __call__(self, event: dict, pipeline: Pipeline, context: Context,
                        ending: bool = True, remain: int = 0) -> AsyncGenerator[dict, None]:
        """Runs the command.
        
        Always yields the received event.
        
        :param event: Latest generated event or `None`
        :param pipeline: Current pipeline instance
        :param context: Current context
        :param ending: True of the pipeline is ending
        :param remain: Remaing number of events
        """
        try:
            await self.target(event, pipeline, context, ending, remain)
        except Exception as error:
            raise CommandError(command=self, message=str(error)) from error
        yield event

    async def target(self, event: dict, pipeline: Pipeline, context: Context,
                        ending: bool = True, remain: int = 0) -> None:
        """MetaCommand target method.

        :param event: Latest generated event or `None`
        :param pipeline: Current pipeline instance
        :param context: Current context
        :param ending: True of the pipeline is ending
        :param remain: Remaing number of events
        """
        pass
