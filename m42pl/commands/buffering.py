import asyncio
from copy import deepcopy
from collections import OrderedDict

from typing import AsyncGenerator

from m42pl.errors import CommandError

from ..event import Event
from .__base__ import AsyncCommand


class BufferingCommand(AsyncCommand):
    """Receives, stores and delays events processing.

    Buffering commands are useful for operations made on events batch
    instead of events stream (e.g. database query, Pandas data sets).

    This default implementation uses a :class:`asyncio.Queue` as its
    internal buffer.

    The method :meth:`__call__` support two additional arguments
    when compared to :class:`AsyncCommand`:

    * :attr:`ending`:   `True` when the pipeline is ending 
                        (i.e. no more events are being generated), 
                        `False` otherwise.
    * :attr:`remain`:   The amount of remaining events in the pipeline.

    When implementing a buffering command, one should either:
    
    * Inherit from this class (:class:`BufferingCommand`)
    * Define a new class with the following members:

      * :meth:`full`:   Returns `True` when the command's buffer is
                        full, `False` otherwise.
      * :meth:`empty`:  Returns `True` when the command's buffer is
                        empty, `False` otherwise.
      * :meth:`store`:  Store an event for future processing.
      * :meth:`clear`:  Clear the command's buffer.
      * :meth:`target`: Process the buffered events.

    :ivar queue_class:  Internal queue class.
    """

    queue_class = asyncio.Queue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxsize = 0

    async def setup(self, event: Event, pipeline: 'Pipeline', maxsize: int):
        if maxsize < 0:
            raise Exception(f'invalid buffer size: maxsize="{maxsize}", reason="Size should be >= 1"')
        self.queue = self.queue_class(maxsize=maxsize)

    async def remain(self) -> int:
        """Returns the amount of remaining events.
        """
        return self.queue.qsize()

    async def __call__(self, event: Event, pipeline: 'Pipeline',
                        ending: bool = False, remain: int = 0, 
                        *args, **kwargs) -> AsyncGenerator[Event, None]:
        """Receives, stores and process events in accordance with the
        pipeline state and buffer limits.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        :param ending:      `True` if the pipeline is ending,
                            `False` otherwise
        :param remain:      Amount of remaining events
        """
        try:
            # Always stores the new event if it is not None
            if event:
                await self.store(event, pipeline)
            # Process buffered events when:
            # * no event has been received (this indicates a pipeline wakeup)
            # * the pipeline is ending
            # * the internal buffer is full
            if not event or (ending and remain == 0) or await self.full():
                async for event in self.target(pipeline):
                    yield event
                await self.clear()
        except Exception as error:
            raise CommandError(command=self, message=str(error))

    async def full(self) -> bool:
        """Returns `True` when the buffer is full, `False` otherwise.
        """
        # print(f'{self} -> is queue full: {self.queue.full()}')
        return self.queue.full()
    
    async def empty(self) -> bool:
        """Returns `True` when the buffer is empty, `False` otherwise.
        """
        return not (await self.full())
    
    async def store(self, event: Event, pipeline: 'Pipeline') -> None:
        """Stores the received `event`.

        The method takes care of copying the event before storing it to
        the internal buffer.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        await self.queue.put(deepcopy(event))
    
    async def clear(self) -> None:
        """Clears the buffer.

        The default implementation does nothing sinc the events are
        `pop`-ed out of the internal buffer.
        """
        pass

    async def target(self, pipeline: 'Pipeline') -> AsyncGenerator[Event, None]:
        """Yields the received event.

        :param pipeline:    Current pipeline instance
        """
        try:
            while True:
                # print(f'{self} -> processing item')
                yield self.queue.get_nowait()
        except asyncio.QueueEmpty:
            # print(f'{self} -> empty queue reached')
            pass


class DequeBufferingCommand(BufferingCommand):
    """Buffers events and replaces them with their new versions.

    Each event received through :meth:`store` is added to the internal
    :class:`OrderedDict` instance and replace the existing event having
    the same `signature`.
    """

    class OrderedDictQueue(asyncio.Queue):
        """Custom AsyncIO queue based on an OrderedDict.
        """
        def _init(self, maxsize):
            self._queue = OrderedDict()
            self._maxsize = maxsize
        
        def _put(self, item):
            self._queue[item.signature] = item

        def _get(self):
            return self._queue.popitem(last=False)[1]

    queue_class = OrderedDictQueue
