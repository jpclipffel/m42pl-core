import asyncio
from copy import deepcopy
from collections import OrderedDict

from typing import AsyncGenerator

from m42pl.errors import CommandError

from ..event import Event
from .base import AsyncCommand


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
    * Define a new class with the following methods:

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
        self.buffer = self.queue_class(maxsize=maxsize)

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
            if event:
                await self.store(event, pipeline)
            if not event or (ending and remain == 0) or await self.full():
                async for event in self.target(pipeline):
                    yield event
                await self.clear()
        except Exception as error:
            # pipeline.logger.error(str(error))
            # pipeline.logger.exception(error)
            # yield event
            raise CommandError(command=self, message=str(error))

    async def full(self) -> bool:
        """Returns `True` when the buffer is full, `False` otherwise.
        """
        return self.buffer.full()
    
    async def empty(self) -> bool:
        """Returns `True` when the buffer is empty, `False` otherwise.
        """
        return not (await self.full())
    
    async def store(self, event: Event, pipeline: 'Pipeline') -> None:
        """Stores the received `event`.

        :param event:       Current event
        :param pipeline:    Current pipeline instance
        """
        await self.buffer.put(deepcopy(event))
    
    async def clear(self) -> None:
        """Clears the buffer.
        """
        pass

    async def target(self, pipeline: 'Pipeline') -> AsyncGenerator[Event, None]:
        """Yields the received event.

        :param pipeline:    Current pipeline instance
        """
        try:
            while True:
                yield self.buffer.get_nowait()
        except asyncio.QueueEmpty:
            pass


class DequeBufferingCommand(BufferingCommand):
    """Buffering command which keeps only the latest version of events.

    Each event received through :meth:`store` is added to the internal
    :class:`OrderedDict` instance and replace the existing event having
    the same `signature`.

    The replaced events position in the queue is not preserved: if a
    new event replaces event #N, event #N is poped out of the queue and
    the new event is placed at the end of the queue.
    """

    class OrderedDictQueue(asyncio.Queue):
        def _init(self, maxsize):
            self._queue = OrderedDict()
        
        def _put(self, item):
            self._queue.pop(item.signature, None)
            self._queue[item.signature] = deepcopy(item)

        def _get(self):
            i = self._queue.popitem()[1]
            return i

    queue_class = OrderedDictQueue


# class QueueBufferingCommand(BufferingCommand):
#     '''
#     '''
#     def __init__(self, maxlen: int = 0, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.buffer = asyncio.Queue(maxsize=maxlen)
    
#     async def remain(self):
#         return self.buffer.qsize()
    
#     async def full(self):
#         return self.buffer.full()
    
#     async def store(self, event: Event, pipeline: 'Pipeline'):
#         await self.buffer.put(deepcopy(event))
    
#     async def clear(self):
#         pass

#     async def target(self, pipeline: 'Pipeline'):
#         try:
#             while True:
#                 yield self.buffer.get_nowait()
#         except asyncio.QueueEmpty:
#             pass


# class DictBufferingCommand(BufferingCommand):
#     '''Buffers *unique* events in a circular buffer.

#     Duplicated events are filtered: An existing event having the same
#     signature as the new one will be replaced.
#     '''

#     class DequeDict(OrderedDict):
#         def __init__(self, maxlen, *args, **kwargs):
#             self.maxlen = maxlen
#             super().__init__(*args, **kwargs)

#         def __setitem__(self, key, value):
#             # OrderedDict.__setitem__(self, key, value)
#             super().__setitem__(key, value)
#             if self.maxlen and len(self) > self.maxlen:
#                 self.popitem(False)

#     def __init__(self, maxlen: int = 0, *args, **kwargs):
#         '''
#         :param maxlen:  Buffer maximum size.
#                         Defaults to 0 (events are processed immediately).
#         '''
#         super().__init__(*args, **kwargs)
#         self.buffer = self.DequeDict(maxlen=maxlen)

#     async def remain(self):
#         return len(self.buffer)

#     async def full(self):
#         return len(self.buffer) >= self.buffer.maxlen
    
#     async def store(self, event: Event, pipeline: 'Pipeline'):
#         self.buffer[event.signature] = deepcopy(event)
    
#     async def clear(self):
#         self.buffer.clear()

#     async def target(self, pipeline: 'Pipeline'):
#         for _, event in self.buffer.items(): # pylint: disable=not-an-iterable
#             yield event
