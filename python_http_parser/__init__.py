"""
``python_http_parser`` module.
"""

# List the public API of this module.
__all__ = [
    'decode',
    'parse',
]

# The version...
__version__ = '0.4.0'

# Imports.
from . import constants, errors, utils


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
    msg = msg.decode('utf-8') if isinstance(
        msg, (bytes, bytearray)
    ) else msg  # type: str
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
        raise errors.NewlineError(
            'Invalid line breaks! Expected CRLF, received LF.')

    start_line, msg = utils.get_start_line(msg, newline_type)

    if is_response:
        output['http_ver'], output['status_code'], output['status_msg'] = \
            utils.parse_status_line(start_line)
    else:
        output['req_method'], output['req_uri'], output['http_ver'] = \
            utils.parse_request_line(start_line)

    # Find the double newline and split the message.
    head, output['body'] = utils.split_msg(msg, newline_type)

    # Get headers.
    output['raw_headers'], output['headers'] = utils.get_headers(
        head, newline_type, strictness_level
    )

    return output


# Aliases for the above functions.
decode = parse
