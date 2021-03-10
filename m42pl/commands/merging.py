from .streaming import StreamingCommand


class MergingCommand(StreamingCommand):
    """Receives, process and forwards events.
    
    This command type behaves as its parent class
    :class:`StreamingCommand`, but indicates that a splitted pipeline
    must be merged.

    Do **not** try to extends this class to creates a classes like a 
    buffering merging command.
    """
    pass
