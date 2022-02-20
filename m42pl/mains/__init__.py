from .repl import REPL
from .repl2 import REPL2
from .run import Run
from .grammar import Grammar
from .parse import Parse
from .status import Status
from .serve import Serve


commands = [
    REPL,       # Shell-like CLI
    REPL2,
    Run,        # Run script from file
    Grammar,    # Dump M42PL grammar
    Parse,      # Parse a M42PL script
    Status,     # Debug - Dump pipelines status from KVStore
    Serve       # Test - Run pipelines from REST API
]
