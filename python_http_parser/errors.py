"""Error classes that are raised by ``python_http_parser"""
__all__ = [
    'LengthError',
    'ParsingError',
    'FatalParsingError',
    'InvalidStructureError'
]


class LengthError(Exception):
    """LengthError class. Raised when something length-related fails."""

    def __init__(self, *args):
        super().__init__(*args)

        self.code = 'ELENGTH'


class ParsingError(Exception):
    """ParsingError class. The generic "catch-all" error when parsing fails."""

    def __init__(self, *args):
        super().__init__(*args)

        self.code = 'EPARSEFAIL'


class FatalParsingError(Exception):
    """FatalParsingError class. This is raised when parsing fails and absolutely CANNOT go on."""

    def __init__(self, *args):
        super().__init__(*args)

        self.code = 'EPARSEFATAL'

class InvalidStructureError(Exception):
    """InvalidStructureError class.

    This is raise when something does not match the expected structure.
    """

    def __init__(self, *args):
        super().__init__(*args)

        self.code = 'EINVALIDSTRUCT'
