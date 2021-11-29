from re import L
from textwrap import dedent
import uuid
import json
from collections import OrderedDict

from lark import Transformer as LarkTransformer, Discard

import lark.exceptions

import m42pl
import m42pl.errors as errors
from m42pl.commands import Command
from m42pl.pipeline import Pipeline
# from m42pl.kvstores import KVStore
# from m42pl.context import Context


class Script(Command):
    """Base class for M42PL scripts parsing commands.
    """

    _name_      = 'script'
    _grammar_   = OrderedDict({
        'directives': dedent('''\
            COMMENT : "/*" /.*/ "*/" 
            %import common.WS
            %import common.NEWLINE
            %ignore NEWLINE
            %ignore COMMENT
        '''),
        # ---
        'fields_terminals': Command._grammar_['fields_terminals'],
        # ---
        'script_terminals': dedent('''\
            SYMBOL      : ( "+" | "-" | "*" | "/" | "%" | "^" | ":" | "!" | "<" | ">" | "{" | "}" | "(" | ")" | "," | "=" | "==" | ">=" | "<=" | "!=" )
            CMD_NAME.3  : /[a-zA-Z_]+[a-zA-Z0-9_-]*/
        '''),
        # ---
        'fields_rules': Command._grammar_['fields_rules'],
        # ---
        'script_rules': dedent('''\
            space       : WS+
            body        : (field | WS | SYMBOL)+
            block       : "[" (space | commands)? "]"
            blocks      : (block space? ","? space?)+
            command     : space? "|" space? CMD_NAME (body | blocks)*
            commands    : command+
            pipeline    : commands
            start       : pipeline
        ''')
    })

    class Transformer(LarkTransformer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pipelines = OrderedDict()

        def _discard(self, _):
            raise Discard

        def space(self, _):
            raise Discard

        float       = lambda self, items: str(items[0])
        integer     = lambda self, items: str(items[0])
        boolean     = lambda self, items: str(items[0].lower())
        name        = lambda self, items: str(items[0])
        # string      = lambda self, items: str(items[0])
        eval        = lambda self, items: str(items[0])
        jspath      = lambda self, items: str(items[0])
        dotpath     = lambda self, items: str(items[0])
        body        = lambda self, items: ''.join(items) \
                                            .lstrip(' ') \
                                            .rstrip(' ')

        def string(self, items):
            return str(items[0]).replace('\\\n', '')


    def __init__(self, source: str):
        """
        :param source:      Source script
        """
        self.source = source

    def target(self):
        # ---
        # Cleanup source and add a leading '|' if necessary
        source = self.source.lstrip()
        if len(source) >= 2 and source[0:2] != "/*" and source[0] != '|':
            source = f'| {source}'
        # ---
        # Parse and transform source
        try:
            return self._transformer_.transform(
                self._parser_.parse(source)
            )
        # ---
        # Handle errors
        # - Lex and parse errors occurs when parsing the source
        # - Vist errors occurs when building the pipeline
        except (lark.exceptions.LexError,
                lark.exceptions.ParseError,
                lark.exceptions.VisitError) as error:
            # Raise the underlying M42PL error
            if isinstance(error.__context__, errors.M42PLError):
                raise error.__context__ from None
            # Build and raise new M42PL error
            offset = getattr(error, 'pos_in_stream', -1)
            raise errors.ScriptError(
                line=getattr(error, 'line', -1),
                column=getattr(error, 'column', -1),
                # pylint: disable = unsubscriptable-object
                offset=isinstance(offset, tuple) and offset[0] or offset,
                message=str(error)
            ) from error
        # Raise generic M42PL error for unknown error cases
        except Exception as error:
            raise errors.CommandError(
                command=self,
                message=str(error)
            )

    def __call__(self, *args, **kwargs):
        return self.target()


class PipelineScript(Script):
    """Parses a M42PL script and returns a :class:`Pipeline`s map.
    """

    _about_     = 'Parses a M42PL script and returns a pipelines map'
    _syntax_    = '[script=]<script string>'
    _aliases_   = ['script',]

    class Transformer(Script.Transformer):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pipelines_ref = []

        def command(self, items):

            def configure_command(cmd, items):
                if isinstance(cmd, (list, tuple)):
                    for c in cmd:
                        configure_command(c, items)
                else:
                    cmd._lncol_ = items[0].line, items[0].column
                    cmd._offset_ = items[0].pos_in_stream
                    cmd._name_ = command_name

            # Extract command name and body
            command_name = str(items[0])
            command_body = ' '.join(
                filter(
                    None,
                    len(items) > 1 and items[1:] or []
                )
            )
            # Instanciate new command
            try:
                cmd = m42pl.command(command_name).from_script(command_body)
            except Exception as error:
                raise errors.ScriptError(
                    line=items[0].line,
                    column=items[0].column,
                    offset=items[0].pos_in_stream,
                    message=str(error)
                )
            # Setup command instance
            configure_command(cmd, items)
            # Done
            return cmd
        
        def commands(self, items):
            return items

        def pipeline(self, items):
            """Process the main pipeline.

            The main pipeline is the 'enclosing' pipeline.
            """
            # print(f'MAIN PIPELINE !')
            # pipeline_name = str(uuid.uuid4())
            pipeline_name = 'main'
            self.pipelines[pipeline_name] = Pipeline(
                commands=items[0],
                name=pipeline_name
            )
            # Add sub-pipelines references
            self.pipelines[pipeline_name].pipelines_ref = self.pipelines_ref

        def block(self, items):
            """Process a sub-pipeline.

            A sub-pipeline is enclosed between `[` and `]` (thus the
            'block' appelation).
            """
            # print(f'SUB PIPELINE !')
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = Pipeline(
                commands=len(items) > 0 and items[0] or [], 
                name=pipeline_name
            )
            self.pipelines_ref.append(f'@{pipeline_name}')
            return f'@{pipeline_name}'
        
        def blocks(self, items):
            return ', '.join(items)

        def start(self, items):
            # Rename main pipeline to 'main'
            # _, self.pipelines['main'] = self.pipelines.popitem()
            # self.pipelines['main'].name = 'main'
            # Done
            return self.pipelines


class JSONScript(PipelineScript):
    """Parses a M42PL script and returns :class:`dict`.

    The returned :class:`dict` is JSON-serializable.
    """

    _aliases_ = ['script_json',]

    class Transformer(PipelineScript.Transformer):

        def command(self, items):
            command_name = str(items[0])
            command_body = ' '.join(
                filter(
                    None,
                    len(items) > 1 and items[1:] or []
                )
            )
            return {
                'name': command_name,
                'body': command_body
            }

        def pipeline(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = {
                'commands': items[0],
                'name': pipeline_name
            }

        def block(self, items):
            pipeline_name = str(uuid.uuid4())
            self.pipelines[pipeline_name] = {
                'commands': len(items) > 0 and items[0] or [], 
                'name': pipeline_name
            }
            return f'@{pipeline_name}'

        def start(self, items):
            _, self.pipelines['main'] = self.pipelines.popitem()
            self.pipelines['main']['name'] = 'main'
            return self.pipelines

    def target(self, *args, **kwargs):
        return json.dumps(super().target(*args, **kwargs))
