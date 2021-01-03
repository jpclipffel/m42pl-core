from textwrap import dedent

from m42pl.errors import M42PLError


CLIErrorString = dedent('''\
    {header}
    {short_desc}:
    
        {errmsg}

    {location}

        {snippet}
''')



class ErrorRender:
    def __init__(self, error: Exception, source: str = None):
        """
        :param error:   Exception
        :param source:  Source script
        """
        self.error = error
        self.source = source
        self.short_desc = getattr(error, 'short_desc', '')
        self.errmsg = str(error)


class CLIErrorRender(ErrorRender):
    _red = '\033[91m'
    _bold = '\033[1m'
    _reset ='\033[0m'

    @staticmethod
    def begin_offset(source, offset):
        i = offset
        while i > 0 and source[i] != '|':
            i -= 1
        return i
    
    @staticmethod
    def end_offset(source, offset):
        i = offset
        while i < len(source) and source[i] != '|':
            i += 1
        return i

    def __init__(self, error: Exception, source: str = None):
        super().__init__(error, source)
        # Generate header
        self.header = f'{self._red}{self._bold}ERROR | {error.__class__.__name__}{self._reset}'
        # Update description with location
        if (hasattr(self.error, 'line') and hasattr(self.error, 'column')) or hasattr(self.error, 'offset'):
            if self.error.line >= 0 and self.error.column >= 0:
                self.location = f'At line {self.error.line}, column {self.error.column}:'
            else:
                self.location = f'At position {self.error.offset}:'
        else:
            self.location = '---'
        # Generate snippet
        if self.source and hasattr(self.error, 'offset'):
            self.snippet = source[
                CLIErrorRender.begin_offset(source, self.error.offset):
                CLIErrorRender.end_offset(source, self.error.offset)
            ]
        # Generate location
        else:
            self.snippet = ''
    
    def render(self):
        return CLIErrorString.format(
            header=self.header,
            short_desc=self.short_desc,
            errmsg=self.errmsg,
            location=self.location,
            snippet=self.snippet
        )
