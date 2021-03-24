"""
``python_http_parser`` module.
"""

# List the public API of this package.
__all__ = [
    'decode',
    'parse'
]
# The version...
__version__ = '0.3.0'

# Imports.
import python_http_parser.constants as constants
import python_http_parser.errors as errors
import python_http_parser.utils as utils


def parse(msg, strictness_level=constants.PARSER_NORMAL, is_response=False):
    """Parse the specified message.

    Arguments:\n
    ``msg`` -- The HTTP message to parse. Must be ``bytes``, a ``bytearray``, or
    a ``str``.\n
    ``strictness_level`` -- How strict to be while parsing. Must be 1, 2, or 3
    (``constants.PARSER_LENIENT``, ``constants.PARSER_NORMAL``, ``constants.PARSER_STRICT``).

    Returns:
    ```
    {
      # The following 4 fields are either None or their specified type depending
      # on whether the message was a response or request message.
      'status_code': Optional[int],
      'status_msg': Optional[str],
      'req_method': Optional[str],
      'req_uri': Optional[str],
      'http_ver': float, # The HTTP version (e.g. 1.1, 1.0...)
      # Dictionary of headers that were received.
      # Duplicates are concatenated into a list.
      'headers': Dict[str, Union[str, list]],
      'raw_headers': List[str], # The headers just as was received.
      # If we encountered double newlines, the characters after those double
      # newlines, if any.
      'body': Optional[str]
    }
    ```
    """
    msg = msg.decode('utf-8') if isinstance(msg, (bytes, bytearray)) else msg  # type: str
    newline_type = ''
    output = {
        'status_code': None,
        'status_msg': None,
        'req_method': None,
        'req_uri': None,
        'http_ver': None,
        'headers': {},
        'raw_headers': [],
        'body': None
    }

    # Get the first line and the newline type.
    newline_type = utils.get_newline_type(msg)

    # PARSER_STRICT does not allow LF.
    if newline_type != '\r\n' and strictness_level == constants.PARSER_STRICT:
        raise TypeError('Invalid line breaks! Expected CRLF, received LF.')

    start_line = msg[:msg.find(newline_type)]
    # Remove the start line from memory.
    msg = msg[msg.find(newline_type):]
    if not start_line:
        # Leading line break detected. Ignore.
        # There might also be other line breaks, so keep looking for a line
        # that is NOT empty.
        while not start_line:
            msg = msg[msg.find(newline_type):]
            start_line = msg[:msg.find(newline_type)]

    if is_response:
        ver, status, status_msg = utils.parse_status_line(start_line)
        output['status_code'] = int(status)
        output['status_msg'] = status_msg
        output['http_ver'] = float(ver)
    else:
        method, uri, ver = utils.parse_request_line(start_line)
        output['req_uri'] = uri
        output['req_method'] = method
        output['http_ver'] = float(ver)

    # Find the double newline.
    double_newline = msg.find(newline_type + newline_type)
    if not bool(~double_newline):
        raise errors.FatalParsingError('Missing double newline!')

    # Now, split the message.
    head = msg[:double_newline]
    body = msg[double_newline + len(newline_type + newline_type):]
    output['body'] = body

    # Get headers.
    output['raw_headers'], output['headers'] = utils.get_headers(
        head, newline_type, strictness_level
    )

    return output


# Aliases for the above functions.
decode = parse
