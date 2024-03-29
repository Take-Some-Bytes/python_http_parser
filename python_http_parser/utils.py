"""
``utils`` module with utility parsing functions.
"""

__all__ = [
    'split_msg',
    'get_newline_type',
    'get_headers',
    'parse_status_line',
    'parse_request_line',
    'parse_header_line',
]
import collections
import re

from . import constants, errors

SplitMessage = collections.namedtuple('SplitRequest', ['head', 'body'])
RequestLine = collections.namedtuple(
    'RequestLine', ['method', 'uri', 'version']
)
StatusLine = collections.namedtuple('StatusLine', ['version', 'code', 'msg'])
ConsumedData = collections.namedtuple('ConsumedData', ['data', 'leftovers'])
ParsedHeaders = collections.namedtuple(
    'ParsedHeaders', ['raw_headers', 'headers']
)


def split_msg(msg, newline_type):
    """Split a HTTP message and return the head and body in a list."""
    double_newline = msg.find(newline_type + newline_type)
    if not bool(~double_newline):
        raise errors.NewlineError('Missing double newline!')

    return SplitMessage(
        head=msg[:double_newline],
        body=msg[double_newline+len(newline_type + newline_type):]
    )


def get_start_line(msg, newline_type):
    """Get the start line of a HTTP message.

    Return a ConsumedData namedtuple with the start line in the 'data'
    property and the remaining message in the 'leftovers' property.
    """
    start_line = msg[:msg.find(newline_type)]
    # Remove the start line from the request string.
    msg = msg[msg.find(newline_type):]
    if not start_line:
        # Leading blank line detected. Ignore.
        # There might also be other blank lines, so keep looking for a line
        # that is NOT blank.
        while not start_line:
            msg = msg[msg.find(newline_type):]
            start_line = msg[:msg.find(newline_type)]

    return ConsumedData(start_line, msg)


def get_newline_type(msg):
    """Get the newline type for a HTTP message."""
    # Get the first line and the newline type.
    newline_index = msg.find('\n')
    if not bool(~newline_index):
        raise errors.NewlineError('No newlines found!')

    # Next, check if we have to deal with CRLF.
    if msg[newline_index - 1] == '\r':
        return '\r\n'
    return '\n'


def get_headers(head, newline_type, strictness):
    """Get the headers from the head section of a HTTP message.

    The head parameter must be the part of the HTTP message that came BEFORE the
    double newline.

    Return a list with the raw headers as the first element and parsed headers as the second.
    """
    headers = {}
    raw_headers = []

    for hdr_line in head.split(newline_type):
        try:
            parsed = parse_header_line(hdr_line)
        except errors.LengthError as len_er:
            if strictness != constants.PARSER_STRICT:
                continue
            raise len_er
        except errors.ParsingError as ex:
            if strictness == constants.PARSER_LENIENT:
                continue
            raise ex

        raw_headers.append(parsed['raw'][0])
        raw_headers.append(parsed['raw'][1])

        # Duplicates must be merged into a list, even if it's not
        # valid to do so. We'll handle the invalid duplicates somewhere else.
        if parsed['name'] in headers:
            hdr_val = headers[parsed['name']]

            if isinstance(hdr_val, list):
                hdr_val.append(parsed['value'])
                headers[parsed['name']] = hdr_val
            else:
                headers[parsed['name']] = [hdr_val, parsed['value']]
        else:
            headers[parsed['name']] = parsed['value']

    return ParsedHeaders(raw_headers, headers)


def parse_status_line(string):
    """
    Parse a HTTP status line and return the HTTP version, status code, and status message as a list.
    """
    if re.match(constants.HTTP_STATUS_LINE_REGEX, string, flags=re.ASCII):
        return StatusLine(
            # HTTP version.
            float(string[5:8]),
            # HTTP status code.
            int(string[9:12]),
            # Rest is HTTP status message.
            string[13:]
        )

    raise errors.InvalidStructureError(
        'Structure of status line is invalid!'
    )


def parse_request_line(string):
    """Parse a HTTP request line and return the HTTP method, URI, and version as a list."""
    if re.match(constants.HTTP_REQUEST_LINE_REGEX, string, flags=re.ASCII):
        split = string.split(' ')
        if len(split) == 3:
            split[2] = float(split[2][5:])
            return RequestLine(*split)

    raise errors.InvalidStructureError(
        'Structure of request line is invalid!'
    )


def parse_header_line(hdr_line):
    """Parse a single header line.

    The ``hdr_line`` argument MUST be a string. Take care to remove any newlines
    the header line had. This function will not remove them.

    Returns a dict with the following structure:
    ```
    {
      'name': str,
      'value': str,
      'raw': [str, str]
    }
    ```
    """
    if not isinstance(hdr_line, str):
        raise TypeError('hdr_line is not a string!')
    if len(hdr_line) < 3:
        # python_http_parser, when not in lenient mode, does not accept
        # empty header values, so the shortest header line is ``a:b``
        raise errors.LengthError('Header line is too short!')

    if hdr_line[0].isspace():
        # Whitespace at beginning of header line is not allowed.
        raise errors.ParsingError(
            'Whitespace detected at beginning of header line!')

    colon_pos = hdr_line.find(':')
    if not ~colon_pos:
        raise errors.ParsingError(
            'Invalid header line! Missing colon between header name and value.')

    # Check if there is a space between the colon and the header name.
    if hdr_line[colon_pos - 1].isspace():
        raise errors.ParsingError(
            'Whitespace detected between header name and colon!')

    # Next, check if the header value uses 'obsolete fold'.
    # if hdr_line

    hdr_name = hdr_line[:colon_pos]
    hdr_val = hdr_line[colon_pos + 1:]

    return {
        'name': hdr_name.lower(),
        'value': hdr_val,
        # 'raw' contains the header name and value just as we received them.
        'raw': [hdr_name, hdr_val]
    }
