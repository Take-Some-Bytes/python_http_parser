"""``python_http_parser`` constants."""

from enum import Enum, IntEnum
from string import ascii_letters, digits, hexdigits

# Constants.
PARSER_STRICT = 3
PARSER_NORMAL = 2
PARSER_LENIENT = 1


class ParserStrictness(IntEnum):
    """An enum describing the strictness levels of the HTTP parser."""
    # These have the same values as the plain int constants above
    # for compatibility reasons.
    LENIENT = 1
    NORMAL = 2
    STRICT = 3


HTTP_STATUS_LINE_REGEX = r'^HTTP/\d\.\d [0-9]{3} (?:\w| )*$'
HTTP_REQUEST_LINE_REGEX = \
    r'^[0-9a-zA-Z!#$%&\'*+\-.^_`|~]+ (?:/(?:[!#$&-;=?-[\]_a-z~]|%[0-9a-fA-F]{2})*|\*) HTTP/\d\.\d$'

# Parser states:
class ParserState(Enum):
    """An Enum describing the state of the HTTPParser."""
    EMPTY = 0
    DONE = 1
    HAD_ERROR = 2
    RECEIVING_METHOD = 3
    RECEIVING_URI = 4
    RECEIVING_STATUS_CODE = 5
    RECEIVING_REASON = 6
    PARSING_VERSION = 7
    PARSING_HEADER_NAME = 8
    PARSING_HEADER_VAL = 9
    DONE_STARTLINE = 10
    DONE_HEADERS = 11
    PROCESSING_BODY = 12


# All the characters in a HTTP token.
TOKENS = ''.join([
    # IMO it doesn't really make sense to allow a bunch of random
    # punctuation in a HTTP token.
    '!', '#', '$', '%', '&', "'", '*', '+',
    '.', '^', '_', '`', '|', '~', '-',
    *list(digits), *list(ascii_letters)
]).encode('utf-8')
# All the characters in a HTTP URI.
URI_CHARS = ''.join([
    # For percent encoding.
    '%',
    # Reserved (but still allowed).
    # We don't actually parse the URI--we just receive it.
    ':', '/', '?', '#', '[', ']', '@', '!', '$',
    '&', "'", '(', ')', '*', '+', ',', ';', '=',
    # Unreserved.
    '-', '.', '_', '~',
    *list(ascii_letters),
    *list(digits)
]).encode('utf-8')
# Space, horizontal tab, and all visible printing characters.
VCHAR_OR_WSP = b''.join([
    b' ', b'\t',
    *list(map(lambda byte: bytes([byte]), range(0x21, 0x7f)))
])
# Characters in obsolete text.
OBS_TXT = b''.join(map(lambda byte: bytes([byte]), range(0x80, 0x100)))
# All normal digits.
DIGITS = digits.encode('utf-8')
# All hexidecimal digits.
HEX_DIGITS = hexdigits.encode('utf-8')

# Hard limit of 65535 characters in a HTTP URI.
MAX_URI_LEN = 65535
# Hard limit of 64 characters in a HTTP request method.
MAX_REQ_METHOD_LEN = 64
# Hard limit of 1024 characters in a HTTP reason phrase.
MAX_REASON_LEN = 1024
# Hard maximum size for each chunk in a chunked HTTP body (16MiB).
MAX_CHUNK_SIZE = 16777216
# The maximum amount of digits a chunk size could have. Since we accept chunk
# sizes up to 16MiB, it must be 7 (0x1000000 == 16MiB).
MAX_CHUNK_SIZE_DIGITS = 7
# Chunk extensions may only be 4 KiB.
MAX_CHUNK_EXTENSION_SIZE = 4096
# Header names may only be 128 characters long.
MAX_HEADER_NAME_LEN = 128
# Header values may only be 16KiB large.
MAX_HEADER_VAL_SIZE = 16384
