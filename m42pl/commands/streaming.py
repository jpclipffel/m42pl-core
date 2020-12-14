from typing import AsyncGenerator

from ..event import Event
from .base import AsyncCommand


class StreamingCommand(AsyncCommand):
    '''Receives, process and yields events.
    '''

    async def __call__(self, event: Event, pipeline: 'Pipeline',
                        *args, **kwargs) -> AsyncGenerator[Event, None]:
        '''Runs the command.
        
        :param event:       Current event
        :param pipeline:    Current pipeline instance
        '''
        if event:
            try:
                async for event in self.target(event, pipeline):
                    yield event
            except Exception as error:
                # pipeline.logger.error(str(error))
                pipeline.logger.exception(error)
                yield event
        else:
            yield event

    async def target(self, event: Event, pipeline: 'Pipeline') -> AsyncGenerator[Event, None]:
        '''Process and yields events.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        '''
        yield event
