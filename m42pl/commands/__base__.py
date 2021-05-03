from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator, Tuple

if TYPE_CHECKING:
    from m42pl.pipeline import Pipeline

import re
import logging
from collections import OrderedDict
from textwrap import dedent
from lark import Lark, Transformer as _Transformer, Discard

from m42pl.event import Event

from . import ALIASES


# Module-level logger
logger = logging.getLogger('m42pl.commands')


class Command():
    """Base command class.

    **DO NOT INHERIT FROM THIS CLASS** when implementing a new command.
    
    This base class provides the following functionalities:

    * Default metadata fields (*about*, *syntax*, etc.)
    * Commands registration
    * Default parsing tools (grammar, transformer, parser)
    * Default serialization
    * Default chunking

    This base class *does not* provides:

    * The commands calling machinery

    The following attributes must be set by the command developer:

    :ivar _about_:          Command short description
    :ivar _syntax_:         Command syntax
    :ivar _aliases_:        List of command names
    :ivar _grammar_:        Command grammar blocks
    :ivar Transformer:      Lark transformer class
    :ivar logger:           Logger instance

    The following attributes are set at run time:

    :ivar _ebnf_:           Command grammar (string)
    :ivar _transformer_:    Lark transformer instance
    :ivar _parser_:         Lark parser
    :ivar _lncol_:          Common position (line, col) in source script
    :ivar _offset_:         Command offset in source script
    :ivar _name_:           Command name in source script
    """

    _about_     = ''
    _syntax_    = ''
    _aliases_   = [] # type: list[str]
    # pylint: disable=anomalous-backslash-in-string
    _grammar_   = OrderedDict({
        # ---
        'directives': dedent('''\
            COMMENT : "/*" /.*/ "*/" 
            %import common.WS
            %import common.NEWLINE
            %ignore NEWLINE
            %ignore WS
            %ignore COMMENT
        '''),
        # ---
        'eval_terminals': dedent('''\
            // eval_terminals
            EVAL_SYMBOLS    : ( "+" | "-" | "*" | "/" | "%" | "^" | "!" | ">=" | "<=" | "<" | ">" | "==" | "!=" )
        '''),
        # ---
        'fields_terminals': dedent('''\
            // fields_terminals
            DIGIT       : "0".."9"
            FLOAT       : ("-")? DIGIT+ "." DIGIT+
            INTEGER     : ("-")? DIGIT+
            NAME        : /[a-zA-Z_]+[a-zA-Z0-9_-]*/
            STRING      : /"(?:[^"\\\\]|\\\\.|\n)*"/xs | /'(?:[^'\\\\]|\\\\.|\n)*'/xs
            EVAL        : /`(?:[^`\\\\]|\\\\.)*`/
            JSPATH      : /\{.*\}/
            DOTPATH     : NAME ( "." NAME )+
            PIPEREF     : /@[a-zA-Z0-9_-]+/
        '''),
        # ---
        'collections_terminals': dedent('''\
            // collections_terminals
            FUNC_START.2    : /[a-zA-Z]+[a-zA-Z0-9_]*\(/
            SEQN_START.1    : "("
            COLLECTION_END  : ")"
        '''),
        # ---
        'arguments_terminals': dedent('''\
            // arguments_terminals
            KWARG   : /[a-zA-Z_]+[a-zA-Z0-9_]*\s*=/
        '''),
        # ---
        'eval_rules': dedent('''\
            symbol      : EVAL_SYMBOLS
            operation   : (field|function) (symbol (field|function))+
        '''),
        # ---
        'fields_rules': dedent('''\
            // fields_rules
            ?field  : FLOAT     -> float
                    | INTEGER   -> integer
                    | STRING    -> string
                    | EVAL      -> eval
                    | JSPATH    -> jspath
                    | NAME      -> name
                    | DOTPATH   -> dotpath
                    | PIPEREF   -> piperef
        '''),
        # ---
        # 'collections_rules': dedent('''\
        #     // collections_rules
        #     function    : FUNC_START ((field | collection) ","?)* COLLECTION_END
        #     sequence    : SEQN_START ((field | collection) ","?)* COLLECTION_END
        #     ?collection : function
        #                 | sequence
        # '''),
        'collections_rules': dedent('''\
            // collections_rules
            function    : FUNC_START ((field | collection | operation | EVAL_SYMBOLS) ","?)* COLLECTION_END
            sequence    : SEQN_START ((field | collection | EVAL_SYMBOLS) ","?)* COLLECTION_END
            ?collection : function
                        | sequence
        '''),
        # ---
        'arguments_rules': dedent('''\
            // arguments_rules
            arg         : (field | collection)
            kwarg       : KWARG (field | collection)
            args        : (arg ","?)+
            kwargs      : (kwarg ","?)+
            arguments   : args? ","? kwargs?
        '''),
        # ---
        'piperefs_rules': dedent('''\
            // piperef_rules
            piperef     : PIPEREF
            piperefs    : (piperef ","?)+
        '''),
        # ---
        'start': dedent('''\
            // start
            start   : arguments
        ''')
    })


    class Transformer(_Transformer):
        """Generic Lark transformer.
        """

        def _discard(self, _):
            raise Discard
        
        # comment_rules
        comment     = _discard

        # fields_rules
        float       = lambda self, items: float(items[0])
        integer     = lambda self, items: int(items[0])
        boolean     = lambda self, items: str(items[0].lower()) in ['true', 'yes']
        name        = lambda self, items: str(items[0])
        string      = lambda self, items: str(items[0])
        eval        = lambda self, items: str(items[0])
        jspath      = lambda self, items: str(items[0])
        dotpath     = lambda self, items: str(items[0])

        # eval_rules
        symbol      = lambda self, items: str(items[0])
        operation   = lambda self, items: ' '.join([str(i) for i in  items])

        # collections_rules
        function    = lambda self, items: f'{items[0]}{", ".join([str(i) for i in items[1:-1]])}{items[-1]}'  # print(f'function --> {items}')
        # sequence    = lambda self, items: f'{items[0]}{" ".join([str(i) for i in items[1:-1]])}{items[-1]}'
        sequence    = lambda self, items: len(items) > 2 and items[1:-1] or []

        # arguments_rules
        arg         = lambda self, items: items[0]
        kwarg       = lambda self, items: { str(items[0].rstrip('=').rstrip(' ')): items[1] }
        args        = lambda self, items: items
        kwargs      = lambda self, items: items

        def arguments(self, items):
            args = []
            kwargs = {}
            for itemset in items:
                for item in itemset:
                    if isinstance(item, dict):
                        kwargs.update(item)
                    else:
                        args.append(item)
            # print(f'arguments --> {args}, {kwargs}')
            return args, kwargs

        # piperefs_rules
        piperef         = lambda self, items: str(items[0])
        piperefs        = lambda self, items: items

        # start
        start           = lambda self, items: items[0]


    logger.info(f'building generic command grammar')
    _ebnf_ = '\n'.join([block for _, block in _grammar_.items()])

    logger.info(f'creating generic command parser')
    _parser_ = Lark(_ebnf_, regex=True, parser='lalr')

    logger.info(f'creating generic command transformer')
    _transformer_ = Transformer()

    # Default line & column and offset position in source script
    _lncol_ = (-1, -1)
    _offset_ = -1

    # Command name (as wrote in the script)
    _name_ = ''

    @classmethod
    def from_script(cls, data: str) -> Command:
        """Returns a new :class:`Command` from a M42PL command.

        The new :class:`Command` instance is built by parsing the given
        :param:`data` with the command :ivar:`_transformer_`.
        
        :param data:    M42PL command
        """
        logger.info(f'instanciating command from script: cls="{cls.__name__}"')
        if data and len(data):
            logger.debug('parsing command script: cls="{}", data="{}"'.format(cls.__name__, data.replace('"', '\\"')))
            args, kwargs = cls._transformer_.transform(cls._parser_.parse(data))
            return cls(*args, **kwargs)
        else:
            logger.debug(f'no command script to parse: cls="{cls.__name__}"')
            return cls()

    @classmethod
    def from_dict(cls, data: dict) -> Command:
        """Returns a new :class:`Command` from a :class:`dict`.
        
        The source map :param:`data` must match with the following map:

        .. code-block:: Python

            {
                'args': [],     # Command's arguments list
                'kwargs': {}    # Command's keyword arguments map
            }
        
        :param data:    :class:`dict` instance
        """
        return object.__new__(cls).__init__(
            *data.get('args', []), 
            **data.get('kwargs', {})
        )

    def __init_subclass__(cls, **kwargs):
        """Initializes a command inheriting from this class.
        """
        super().__init_subclass__(**kwargs)
        if len(cls._aliases_):
            module = f'{cls.__module__}.{cls.__name__}'
            # ---
            # Register command aliases
            for alias in cls._aliases_:
                # Asserts command alias format
                if len(list(filter(None, re.split(r'[a-zA-Z0-9_]+[a-zA-Z0-9_-]*', str(alias))))):
                    raise Exception(f'invalid command alias: alias="{alias}", command_path="{module}"')
                # Register command alias
                logger.info(f'registering command alias: command="{cls.__name__}", alias="{alias}"')
                ALIASES[alias] = cls
            # ---
            # Build command grammar
            if cls._grammar_ != Command._grammar_:
                logger.info(f'building command grammar from command grammar blocks: command="{cls.__name__}"')
                cls._ebnf_ = '\n'.join([block for _, block in cls._grammar_.items()])
            # ---
            # Build command parser
            if cls._ebnf_ != Command._ebnf_:
                logger.info(f'building command parser: command="{cls.__name__}"')
                cls._parser_ = Lark(cls._ebnf_, regex=True, parser='lalr')
            # ---
            # Setup command transformer
            if cls.Transformer != Command.Transformer:
                logger.info(f'instanciating command transformer: command="{cls.__name__}"')
                cls._transformer_ = cls.Transformer()

    def __init__(self, *args, **kwargs):
        """
        :param args:        Args list to be automatically
                            exported using `to_dict()`
        :param kwargs:      Kwargs map to be automatically
                            exported using `to_dict()`
        
        :ivar logger:       Command instance logger
        :ivar chunk:        Command instance chunk number (starts at 0)
        :ivar chunks:       Number of chunks running in parallel
        :ivar _args:        Automatically exported args list
        :ivar _kwargs:      Automatically exported kwargs list
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._chunk, self._chunks = 0, 1
        self._args, self._kwargs = args, kwargs

    def to_dict(self) -> dict:
        """Returns a JSON-serializable :class:`dict` from the current
        instance.

        The returned :attr:`dict` must be understandable by 
        attr:`from_dict` and match with the following mapping:

        .. code-block:: Python

            {
                'alias': ''     # Command's name / alias
                'args': [],     # Command's arguments list
                'kwargs': {}    # Command's keyword arguments map
            }
        """
        return {
            'alias': self._aliases_[0],
            'args': self._args,
            'kwargs': self._kwargs
        }

    @property
    def chunk(self) -> Tuple[int, int]:
        """Returns the current chunk number and total chunks number.
        """
        return self._chunk, self._chunks
    
    @chunk.setter
    def chunk(self, value: Tuple[int, int]) -> None:
        """Sets the current chunk number and total chunks number.
        """
        self._chunk, self._chunks = value

    @property
    def first_chunk(self) -> bool:
        """Returns `True` if we are in the first chunk,
        `False` otherwise.
        """
        return self._chunk == 0
    
    @property
    def last_chunk(self) -> bool:
        """Returns `True` if we are in the last chunk,
        `False` otherwise.
        """
        return self._chunk == (self._chunks - 1)
    
    @property
    def inter_chunk(self) -> bool:
        """Returns `True` if we are neither in the first or last chunk,
        `False` otherwise.
        """
        return not self.first_chunk and not self.last_chunk


class AsyncCommand(Command):
    """Base asynchrounous command class.

    **DO NOT INHERIT FROM THIS CLASS** when implementing a new command.

    This base class provides the following functionalities:

    * Default :meth:`remain` method
    * Default asynchronous setup
    * Default asynchronous context managers

    This base class *does not* provides:

    * The commands calling machinery
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def remain(self) -> int:
        """Returns the amount of remaining events in the instance.

        This method should be overridden by generating commands and
        buffering commands.
        """
        return 0

    async def setup(self, event: Event, pipeline: Pipeline, *args, **kwargs):
        """Finishes command initialization.

        Unlike :meth:`__init__`, :meth:`setup` is a coroutine and thus
        can perform more advanced operation, such as fields resolution
        (which is an asynchronous operation).

        Generating commands may omit to call :meth:`setup` and let
        their :meth:`target` method performs the initialization since
        they are called only once per pipeline.

        A command's :meth:`setup` should call it's parent's
        :meth:`setup` after its own initialization:

        .. code-block:: Python

            async def setup(self, event, pipeline):
                # <your own setup goes here>
                await super().setup(event, piepeline)

        :param event:       Latest generated event (may be empty)
        :param pipeline:    Current pipeline
        """
        return

    async def __aenter__(self) -> AsyncCommand:
        """Enters the command context.

        Most commands may use this default implementation.
        For late initialization, a command may uses :meth:`setup` which
        receives the current pipeline and initial event.
        """
        self.logger.info('entering command context')
        return self
    
    async def __aexit__(self, *args, **kwargs) -> None:
        """Exits the command context.

        A command which *allocates* external resources such as sockets,
        file descriptors, shared memory, etc. should closes / frees / 
        releases / ... these resources here.
        """
        self.logger.debug('exiting command context')
        return
