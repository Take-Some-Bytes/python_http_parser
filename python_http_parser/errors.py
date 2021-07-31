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
        """LengthError class. Raised when something length-related fails."""
        super().__init__(*args)

        self.code = 'ELENGTH'


class ParsingError(Exception):
    """ParsingError class. The generic "catch-all" error when parsing fails."""

    def __init__(self, *args):
        """ParsingError class. The generic "catch-all" error when parsing fails."""
        super().__init__(*args)

        self.code = 'EPARSEFAIL'


class NewlineError(Exception):
    """NewLineError class. Raised when something related to newlines fails."""

    def __init__(self, *args):
        """NewLineError class. Raised when something related to newlines fails."""
        super().__init__(*args)

        self.code = 'ENEWLINE'


class FatalParsingError(Exception):
    """FatalParsingError class. This is raised when parsing fails and absolutely CANNOT go on."""

    def __init__(self, *args):
        """
        FatalParsingError class. This is raised when parsing fails and absolutely CANNOT go on.
        """
        super().__init__(*args)

        self.code = 'EPARSEFATAL'


class InvalidStructureError(Exception):
    """InvalidStructureError class.

    This is raise when something does not match the expected structure.
    """

    def __init__(self, *args):
        """InvalidStructureError class.

        This is raise when something does not match the expected structure.
        """
        super().__init__(*args)

        self.code = 'EINVALIDSTRUCT'


class DoneError(Exception):
    """DoneError class.

    This is raise when further parsing/processing is attempted on a HTTPParser
    or BodyProcessor that is already finished parsing/processing.
    """

    def __init__(self, *args):
        """DoneError class.

        This is raise when further parsing/processing is attempted on a HTTPParser
        or BodyProcessor that is already finished parsing/processing.
        """
        super().__init__(*args)

        self.code = 'EDONE'


class InvalidVersion(Exception):
    """Invalid byte or character in HTTP version."""

    def __init__(self, *args):
        """Invalid byte or character in HTTP version."""
        super().__init__(*args)

        self.code = 'EHTTPVER'


class InvalidStatus(Exception):
    """Invalid byte or character in HTTP response status."""

    def __init__(self, *args):
        """Invalid byte or character in HTTP response status."""
        super().__init__(*args)

        self.code = 'ESTATUS'


class UnexpectedChar(Exception):
    """UnexpectedChar exception.

    This is raised when an unexpected character appears in a HTTP message.
    """

    def __init__(self, *args):
        """UnexpectedChar exception.

        This is raised when an invalid characters appears in a HTTP message.
        """
        super().__init__(*args)

        self.code = 'ECHAR'


class InvalidToken(Exception):
    """Invalid byte or character in HTTP token."""

    def __init__(self, *args):
        """Invalid byte or character in HTTP token."""
        super().__init__(*args)

        self.code = 'ETOKEN'


class InvalidURI(Exception):
    """Invalid character in URI."""

    def __init__(self, *args):
        """Invalid character in URI."""
        super().__init__(*args)

        self.code = 'EURICHAR'


class InvalidHeaderVal(Exception):
    """Invalid header value."""

    def __init__(self, *args):
        """Invalid header value."""
        super().__init__(*args)

        self.code = 'EHEADERVAL'


class InvalidChunk(Exception):
    """Invalid chunk."""

    def __init__(self, *args):
        """Invalid chunk."""
        super().__init__(*args)

        self.code = 'ECHUNK'


class InvalidChunkSize(Exception):
    """Invalid chunk size."""

    def __init__(self, *args):
        """Invalid chunk size."""
        super().__init__(*args)

        self.code = 'ECHUNKSIZE'


class InvalidChunkExtensions(Exception):
    """Invalid chunk extensions."""

    def __init__(self, *args):
        """Invalid chunk extensions."""
        super().__init__(*args)

        self.code = 'ECHUNKEXTS'


class BodyProcessorRequired(Exception):
    """Body Processor required but none set."""

    def __init__(self, *args):
        """Body Processor required but none set."""
        super().__init__(*args)

        self.code = 'EBODYPROCESSOR'
