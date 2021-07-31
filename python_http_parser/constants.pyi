"""``python_http_parser`` constants."""

from enum import Enum, IntEnum
# Literal was added in Python 3.8. We need to support Python 3.6.
from typing_extensions import Literal

# Constants.
PARSER_STRICT: Literal[3]
PARSER_NORMAL: Literal[2]
PARSER_LENIENT: Literal[1]


class ParserStrictness(IntEnum):
    """An enum describing the strictness levels of the HTTP parser."""
    # These have the same values as the plain int constants above
    # for compatibility reasons--same goes for the other IntEnums.
    LENIENT = 1
    NORMAL = 2
    STRICT = 3


HTTP_STATUS_LINE_REGEX: Literal[r'^HTTP/\d\.\d [0-9]{3} (?:\w| )*$']
HTTP_REQUEST_LINE_REGEX: Literal[
    r'^[0-9a-zA-Z!#$%&\'*+\-.^_`|~]+ (?:/(?:[!#$&-;=?-[\]_a-z~]|%[0-9a-fA-F]{2})*|\*) HTTP/\d\.\d$'
]

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


TOKENS: bytes
URI_CHARS: bytes
VCHAR_OR_WSP: bytes
OBS_TXT: bytes
DIGITS: bytes
HEX_DIGITS: bytes
MAX_URI_LEN: Literal[65535]
MAX_REQ_METHOD_LEN: Literal[64]
MAX_REASON_LEN: Literal[1024]
MAX_CHUNK_SIZE: Literal[16777216]
MAX_CHUNK_SIZE_DIGITS: Literal[7]
MAX_CHUNK_EXTENSION_SIZE: Literal[4096]
MAX_HEADER_NAME_LEN: Literal[128]
MAX_HEADER_VAL_SIZE: Literal[16384]
