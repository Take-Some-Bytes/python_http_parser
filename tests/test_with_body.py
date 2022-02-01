"""Testing parsers with HTTP messages that have bodies."""

from typing import List

from . import attach_common_event_handlers, chunk, parser_process_chunks
from .context import python_http_parser


def test_stream_fixed_len():
    """Test the stream parser with a fixed length body."""
    errors = []
    result = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'raw_headers': [],
        'headers': {},
        'body': [],
    }
    msg = b"""\
HTTP/1.1 200 All Good
Content-Length: 13
Cache-Control: no-cache
Content-Type: text/plain

Hello World!
"""

    parser = python_http_parser.stream.HTTPParser(is_response=True)

    def on_headers_complete():
        names: List[str] = []
        values: List[str] = []
        for (i, item) in enumerate(result['raw_headers']):
            if i % 2 == 0:
                # Even keys are field names.
                names.append(item.lower())
            else:
                values.append(item.lower())

        for (key, val) in zip(names, values):
            result['headers'][key] = val

        if b'content-length' in result['headers']:
            body_len = int(result['headers'][b'content-length'])
            parser.has_body(True)
            parser.body_processor(python_http_parser.body.FixedLenProcessor(body_len))

    attach_common_event_handlers(parser, result, errors, True)
    parser.on('headers_complete', on_headers_complete)
    parser.process(msg)

    result['body'] = b''.join(result['body']).decode('utf-8')

    assert len(errors) == 0
    assert parser.has_body()
    assert result['http_version'] == (1, 1)
    assert result['status_code'] == 200
    assert result['reason'] == b'All Good'
    assert len(result['raw_headers']) == 6
    assert len(result['headers']) == 3
    assert result['headers'][b'content-length'] == b'13'
    assert result['body'] == 'Hello World!\n'

def test_stream_fixed_len_chunked():
    """
    Test the stream parser with a fixed length body,
    and a message that doesn't arrive all at once.
    """
    errors = []
    result = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'raw_headers': [],
        'headers': {},
        'body': [],
    }
    msg = b"""\
HTTP/1.1 200 All Good
Content-Length: 13
Cache-Control: no-cache
Content-Type: text/plain

Hello World!
"""

    parser = python_http_parser.stream.HTTPParser(is_response=True)

    def on_headers_complete():
        names: List[str] = []
        values: List[str] = []
        for (i, item) in enumerate(result['raw_headers']):
            if i % 2 == 0:
                # Even keys are field names.
                names.append(item.lower())
            else:
                values.append(item.lower())

        for (key, val) in zip(names, values):
            result['headers'][key] = val

        if b'content-length' in result['headers']:
            body_len = int(result['headers'][b'content-length'])
            parser.has_body(True)
            parser.body_processor(python_http_parser.body.FixedLenProcessor(body_len))

    attach_common_event_handlers(parser, result, errors, True)
    parser.on('headers_complete', on_headers_complete)
    parser_process_chunks(parser, chunk(msg, 4))

    result['body'] = b''.join(result['body']).decode('utf-8')

    assert len(errors) == 0
    assert parser.has_body()
    assert result['http_version'] == (1, 1)
    assert result['status_code'] == 200
    assert result['reason'] == b'All Good'
    assert len(result['raw_headers']) == 6
    assert len(result['headers']) == 3
    assert result['headers'][b'content-length'] == b'13'
    assert result['body'] == 'Hello World!\n'

def test_stream_transfer_chunked():
    """Test the stream parser with a Transfer-Encoding: chunked body."""
    errors = []
    result = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'raw_headers': [],
        'headers': {},
        'body': [],
    }
    msg = b''.join([
        b'HTTP/1.1 200 All Good\r\n',
        b'Transfer-Encoding: chunked\r\n',
        b'Cache-Control: no-cache\r\n',
        b'Content-Type: text/plain\r\n',
        b'\r\n',
        b'5\r\n',
        b'Hello\r\n',
        b'5\r\n',
        b' Worl\r\n',
        b'3\r\n',
        b'd!\n\r\n',
        b'0\r\n',
        b'\r\n'
    ])
    parser = python_http_parser.stream.HTTPParser(is_response=True)

    def on_headers_complete():
        names: List[str] = []
        values: List[str] = []
        for (i, item) in enumerate(result['raw_headers']):
            if i % 2 == 0:
                # Even keys are field names.
                names.append(item.lower())
            else:
                values.append(item.lower())

        for (key, val) in zip(names, values):
            result['headers'][key] = val

        if (b'transfer-encoding' in result['headers']) and (
            result['headers'][b'transfer-encoding'] == b'chunked'
        ):
            parser.has_body(True)
            parser.body_processor(python_http_parser.body.ChunkedProcessor())

    attach_common_event_handlers(parser, result, errors, True)
    parser.on('headers_complete', on_headers_complete)
    parser.process(msg)

    result['body'] = b''.join(result['body']).decode('utf-8')

    assert len(errors) == 0
    assert parser.has_body()
    assert result['http_version'] == (1, 1)
    assert result['status_code'] == 200
    assert result['reason'] == b'All Good'
    assert len(result['raw_headers']) == 6
    assert len(result['headers']) == 3
    assert result['headers'][b'transfer-encoding'] == b'chunked'
    assert result['body'] == 'Hello World!\n'

def test_stream_transfer_chunked_chunked():
    """
    Test the HTTP parser with a chunked body that does not arrive all at
    once. Apologies for the ridiculous name.
    """
    errors = []
    result = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'raw_headers': [],
        'headers': {},
        'body': [],
    }
    msg = b''.join([
        b'HTTP/1.1 200 All Good\r\n',
        b'Transfer-Encoding: chunked\r\n',
        b'Cache-Control: no-cache\r\n',
        b'Content-Type: text/plain\r\n',
        b'\r\n',
        b'5\r\n',
        b'Hello\r\n',
        b'5\r\n',
        b' Worl\r\n',
        b'3\r\n',
        b'd!\n\r\n',
        b'0\r\n',
        b'\r\n'
    ])
    parser = python_http_parser.stream.HTTPParser(is_response=True)

    def on_headers_complete():
        names: List[str] = []
        values: List[str] = []
        for (i, item) in enumerate(result['raw_headers']):
            if i % 2 == 0:
                # Even keys are field names.
                names.append(item.lower())
            else:
                values.append(item.lower())

        for (key, val) in zip(names, values):
            result['headers'][key] = val

        if (b'transfer-encoding' in result['headers']) and (
            result['headers'][b'transfer-encoding'] == b'chunked'
        ):
            parser.has_body(True)
            parser.body_processor(python_http_parser.body.ChunkedProcessor())

    attach_common_event_handlers(parser, result, errors, True)
    parser.on('headers_complete', on_headers_complete)
    parser_process_chunks(parser, chunk(msg, 4))

    result['body'] = b''.join(result['body']).decode('utf-8')

    assert len(errors) == 0
    assert parser.has_body()
    assert result['http_version'] == (1, 1)
    assert result['status_code'] == 200
    assert result['reason'] == b'All Good'
    assert len(result['raw_headers']) == 6
    assert len(result['headers']) == 3
    assert result['headers'][b'transfer-encoding'] == b'chunked'
    assert result['body'] == 'Hello World!\n'
