"""``python_http_parser`` constants."""

# Constants.
PARSER_STRICT = 3
PARSER_NORMAL = 2
PARSER_LENIENT = 1

DEFAULT_MAX_HEADER_SIZE = 8192

HTTP_VER_REGEX = r'^HTTP/\d\.\d$'
HTTP_STATUS_REGEX = r'^ \d{3}$'
HTTP_STATUS_LINE_REGEX = r'^HTTP/\d\.\d [0-9]{3} (?:\w| )*$'
HTTP_STATUS_REQUEST_REGEX = \
    r'^[0-9a-zA-Z!#$%&\'*+\-.^_`|~]+ (?:/(?:[!#$&-;=?-[\]_a-z~]|%[0-9a-fA-F]{2})*|\*) HTTP/\d\.\d$'
