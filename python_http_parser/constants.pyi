"""``python_http_parser`` constants."""

from typing import Literal

# Constants.
PARSER_STRICT: Literal[3]
PARSER_NORMAL: Literal[2]
PARSER_LENIENT: Literal[1]

DEFAULT_MAX_HEADER_SIZE: Literal[8192]

HTTP_VER_REGEX: Literal[r'^HTTP/\d\.\d$']
HTTP_STATUS_REGEX: Literal[r'^\d{3}$']
HTTP_STATUS_LINE_REGEX: Literal[r'^HTTP/\d\.\d [0-9]{3} (?:\w| )*$']
HTTP_STATUS_REQUEST_REGEX: Literal[r'^[0-9a-zA-Z!#$%&\'*+\-.^_`|~]+ (?:/(?:[!#$&-;=?-[\]_a-z~]|%[0-9a-fA-F]{2})*|\*) HTTP/\d\.\d$']
