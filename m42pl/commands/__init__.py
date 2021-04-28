# Commands aliases map
ALIASES = dict()    # type: dict[str, object]


from .__base__ import Command
from .buffering import BufferingCommand, DequeBufferingCommand
from .generating import GeneratingCommand
from .merging import MergingCommand
from .meta import MetaCommand
from .streaming import StreamingCommand
