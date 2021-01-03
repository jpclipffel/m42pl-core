from typing import AsyncGenerator

from m42pl.event import Event
from m42pl.errors import CommandError

from .base import AsyncCommand


class GeneratingCommand(AsyncCommand):
    '''Generates events.

    A generating command also receives an :class:`Event` instance when
    started. This event may:
    
    * Contains the latest event generated in the parent pipeline
    * Be empty (i.e. with no data fields, e.g. `Event(data={})`)
    * Be `None` (then an empty event is generated and used in place)
    '''

    async def __call__(self, event: Event, pipeline: 'Pipeline',
                        *args, **kwargs) -> AsyncGenerator[Event, None]:
        '''Runs the command.

        :param event:       Latest generated event or `None`
        :param pipeline:    Current pipeline instance
        '''
        try:
            async for _event in self.target(event or Event(), pipeline):
                yield _event
        except Exception as error:
            # pipeline.logger.error(str(error))
            # pipeline.logger.exception(error)
            raise CommandError(command=self, message=str(error))
    
    async def target(self, event: Event, pipeline: 'Pipeline',
                        *args, **kwargs) -> AsyncGenerator[Event, None]:
        '''Generates and yields events.

        :param event:       Latest generated event
        :param pipeline:    Current pipeline instance
        '''
        yield
