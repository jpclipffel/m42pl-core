from textwrap import dedent
from inspect import cleandoc


class M42PLError(Exception):
    """Base class for M42PL error.

    :ivar short_desc: Exception short description
    """

    short_desc = 'An error occured'

    def __init__(self, message: str = '', *args, **kwargs):
        super().__init__(message)


class ObjectNotFoundError(M42PLError):
    """Raised when a requested M42PL object cannot be found.

    :ivar kind: Object kind
    :ivar name: Object name
    """

    short_desc = 'An requested object has not been found'

    def __init__(self, kind: str, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        self.name = name


class ScriptError(M42PLError):
    """Base class for errors happening during script parsing.

    :ivar line: Error line number in source script
    :ivar column: Error column number in source script
    :ivar offset: Error offset in source script
    """

    short_desc = 'An error occured while parsing the source script'

    def __init__(self, line: int = -1, column: int = -1, offset: int = -1,
                    *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = line
        self.column = column
        self.offset = offset


class CommandError(M42PLError):
    """Raised when a command fails during its execution.

    :ivar line: Error line number in source script
    :ivar column: Error column number in source script
    :ivar offset: Error offset in source script
    :ivar name: Command name
    """

    short_desc = 'An error occured during a command execution'

    def __init__(self, command, *args, **kwargs):
        """
        :param command: Command instance
        """
        super().__init__(*args, **kwargs)
        self.line = command._lncol_[0]
        self.column = command._lncol_[1]
        self.offset = command._offset_
        self.name = command._name_


class FieldError(M42PLError):
    def __init__(self, field_name, message):
        super().__init__(message)
        self.field_name = field_name


class FieldInitError(FieldError):
    def __init__(self, field_name, message):
        super().__init__(field_name, f'failed to initialize field: {message}')


class DispatcherError(M42PLError):
    """Base class for errors happening in dispatchers init or run.
    """

    short_desc = 'A dispatcher error occured'

    def __init__(self, dispatcher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = dispatcher


class EncodingError(M42PLError):
    short_desc = 'An encoding error occured'

    def __init__(self, encoder, message, *args, **kwargs):
        """
        :param encoder:     Encoder instance
        """
        super().__init__(
            (
                f'''Encoder "{encoder._aliases_[0]}" failed to '''
                f'''encode data: {message}'''
            ),
            *args,
            **kwargs
        )
        self.encoder = encoder


class DecodingError(M42PLError):
    short_desc = 'An decoding error occured'

    def __init__(self, encoder, message, *args, **kwargs):
        """
        :param encoder: Encoder instance
        """
        super().__init__(
            (
                f'''Encoder "{encoder._aliases_[0]}" failed to '''
                f'''decode data: {message}'''
            ),
            *args,
            **kwargs
        )
        self.encoder = encoder
