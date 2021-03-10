from typing import AsyncGenerator

from m42pl.errors import CommandError

from ..event import Event
from .base import AsyncCommand


class MetaCommand(AsyncCommand):
    """Controls the events pipeline.
    """

    async def __call__(self, event: Event, pipeline: 'Pipeline',
                        *args, **kwargs) -> AsyncGenerator[Event, None]:
        """Runs the command.
        
        Always yield back the received event.
        
        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        try:
            await self.target(event, pipeline)
        except Exception as error:
            raise CommandError(command=self, message=str(error)) from error
        yield event

    async def target(self, event: Event, pipeline: 'Pipeline') -> None:
        """Dummy MetaCommand target method.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        pass
