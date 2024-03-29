from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline
    from m42pl.context import Context

import asyncio
from copy import deepcopy
from collections import OrderedDict

from m42pl.event import signature
from m42pl.errors import CommandError

from .__base__ import AsyncCommand


class BufferingCommand(AsyncCommand):
    """Receives, stores and delays events processing.

    Buffering commands are useful for operations made on events batch
    instead of events stream (e.g. database query, Pandas data sets).

    This default implementation uses a :class:`asyncio.Queue` as its
    internal buffer.

    The method :meth:`__call__` support two additional arguments
    when compared to :class:`AsyncCommand`:

    * `ending`: `True` when the pipeline is ending (i.e. no
      more events are being generated), `False` otherwise
    * `remain`: The amount of remaining events in the pipeline

    When implementing a buffering command, one should either:
    
    * Inherit from this class (:class:`BufferingCommand`)
    * Define a new class with the following members:

      * :meth:`full`:   Returns `True` when the command's buffer is
        full, `False` otherwise
      * :meth:`empty`:  Returns `True` when the command's buffer is
        empty, `False` otherwise
      * :meth:`store`:  Store an event for future processing
      * :meth:`clear`:  Clear the command's buffer
      * :meth:`target`: Process the buffered events

    :ivar queue_class:  Internal queue class
    """

    queue_class = asyncio.Queue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxsize = 0
        self.hits = 0

    async def setup(self, event: dict, pipeline: Pipeline, context: Context,
                        maxsize: int = 1) -> None: # type: ignore[override]
        """
        :param maxsize:     Internal buffer maximum size
        """
        if maxsize < 0:
            raise Exception((
                f'invalid buffer size: maxsize="{maxsize}", '
                f'reason="Size should be >= 1"'
            ))
        self.queue: asyncio.Queue = self.queue_class(maxsize=maxsize)
        self.maxsize = maxsize

    async def remain(self) -> int:
        """Returns the amount of remaining events.
        """
        return self.queue.qsize()

    async def ready(self, event: dict, pipeline: Pipeline, ending: bool,
                        remain: int) -> bool:
        """Returns True if the queue is ready to be empited and yielded.

        Queue is ready when:
        * no event has been received (this indicates a pipeline wakeup)
        * the pipeline is ending
        * the internal buffer is full
        """
        if (
            not event                       # No event is received
            or (ending and remain == 0)     # Pipeline is ending
            or await self.full()            # Queue is full
        ):
            return True
        return False

    async def __call__(self, event: dict, pipeline: Pipeline,
                        context: Context, ending: bool = False,
                        remain: int = 0) -> AsyncGenerator[dict, None]:
        """Receives, stores and process events in accordance with the
        pipeline state and buffer limits.

        :param event: Latest generated event or `None`
        :param pipeline: Current pipeline instance
        :param context: Current context
        :param ending: True of the pipeline is ending
        :param remain: Remaing number of events
        """
        try:
            # Always stores the new event if it is not None
            if event:
                await self.store(event, pipeline)
                self.hits += 1
            # Process buffered events when:
            # * no event has been received (this indicates a pipeline wakeup)
            # * the pipeline is ending
            # * the internal buffer is full
            # * the maximum count of event is reached
            # If queue should be emptied, do it
            if await self.ready(event, pipeline, ending, remain):
                async for event in self.target(pipeline):
                    yield event
                await self.clear()
                self.hits = 0
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
    
    async def store(self, event: dict, pipeline: Pipeline) -> None:
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

    async def target(self, pipeline: Pipeline) -> AsyncGenerator[dict, None]:
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
        
        def _put(self, event):
            self._queue[signature(event)] = event

        def _get(self):
            return self._queue.popitem(last=False)[1]

    queue_class = OrderedDictQueue
