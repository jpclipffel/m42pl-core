class M42PLError(Exception):
    pass


class FieldError(M42PLError):
    def __init__(self, field_name, message):
        super().__init__(message)
        self.field_name = field_name


class FieldInitError(FieldError):
    def __init__(self, field_name, message):
        super().__init__(field_name, f'failed to initialize field: {message}')
