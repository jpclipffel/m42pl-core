from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline
    from m42pl.context import Context

from m42pl.event import Event
from m42pl.errors import CommandError

from .__base__ import AsyncCommand


class GeneratingCommand(AsyncCommand):
    """Generates events.

    A generating command also receives an :class:`dict` instance when
    started. This event may:
    
    * Contains the latest event generated in the parent pipeline
    * Be empty (i.e. with no data fields, e.g. `dict(data={})`)
    * Be `None` (then an empty event is generated and used in place)
    """

    async def __call__(self, event: dict, pipeline: Pipeline, context: Context,
                        *args, **kwargs) -> AsyncGenerator[dict|None, None]:
        """Runs the command.

        :param event: Latest generated event or `None`
        :param pipeline: Current pipeline instance
        :param context: Current context
        """
        try:
            async for _event in self.target(event or Event(), pipeline, context):
                yield _event
        except Exception as error:
            raise CommandError(command=self, message=str(error)) from error

    async def target(self, event: dict, pipeline: Pipeline,
                        context: Context ) -> AsyncGenerator[dict|None, None]:
        """Generates and yields events.

        :param event: Latest generated event or `None`
        :param pipeline: Current pipeline instance
        :param context: Current context
        """
        yield None
