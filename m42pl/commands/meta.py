from typing import AsyncGenerator

from m42pl.errors import CommandError

from ..event import Event
from .base import AsyncCommand


class MetaCommand(AsyncCommand):
    '''Controls the events pipeline.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def __call__(self, event: Event, pipeline: 'Pipeline', *args, **kwargs) -> AsyncGenerator[Event, None]:
        '''Calls the underlying `target` function.
        
        The input event is always yielded.
        
        :param event:       Current event
        :param pipeline:    Current pipeline instance
        '''
        try:
            await self.target(event, pipeline)
        except Exception as error:
            # pipeline.logger.error(str(error))
            # pipeline.logger.exception(error)
            raise CommandError(command=self, message=str(error))
        yield event

    async def target(self, event: Event, pipeline: 'Pipeline') -> AsyncGenerator[Event, None]:
        '''Dummy method; Does nothing.
        
        This method should be overwriten by the command implementation.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        '''
        pass
