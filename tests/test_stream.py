"""Testing the stream/event based parser."""

from . import attach_common_event_handlers, chunk, parser_process_chunks
from .context import python_http_parser


def test_req():
    """
    Test the stream/event based parser with a HTTP request that conforms to RFC7230
    """
    errors = []
    results = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b"""\
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Some-random-dude
X-Token: Trash::more_trash::bananas

"""
    parser = python_http_parser.stream.HTTPParser()

    attach_common_event_handlers(parser, results, errors, False)
    parser.process(msg)

    assert len(errors) == 0
    assert parser.finished()
    assert results['req_method'] == 'GET'
    assert results['req_uri'] == '/index.html'
    assert results['http_version'] == (1, 1)
    assert len(results['raw_headers']) == 6


def test_req_extra_newlines():
    """
    Test the event-based parser with a HTTP request that has preceding empyt lines.
    """
    errors = []
    results = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b"""\



GET /more-newlines.html HTTP/1.1
Host: localhost:8080
User-Agent: Test runner/1.99999999999999999
Accept: text/*

"""
    parser = python_http_parser.stream.HTTPParser()

    attach_common_event_handlers(parser, results, errors, False)
    parser.process(msg)

    assert len(errors) == 0
    assert parser.finished()
    assert results['req_method'] == 'GET'
    assert results['req_uri'] == '/more-newlines.html'
    assert results['http_version'] == (1, 1)
    assert len(results['raw_headers']) == 6


def test_chunked_req():
    """
    Test the stream/event based parser with a HTTP request that doesn't arrive
    at once.
    """
    errors = []
    results = {
        'req_method': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b"""\
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Some-random-dude
X-Token: Trash::more_trash::bananas

"""
    parser = python_http_parser.stream.HTTPParser()

    attach_common_event_handlers(parser, results, errors, False)
    parser_process_chunks(parser, chunk(msg, 4))

    assert len(errors) == 0
    assert parser.finished()
    assert results['req_method'] == 'GET'
    assert results['req_uri'] == '/index.html'
    assert results['http_version'] == (1, 1)
    assert len(results['raw_headers']) == 6


def test_res():
    """
    Test the stream/event based parser with a HTTP response that conform to RFC7230
    """
    errors = []
    results = {
        'reason': None,
        'status_code': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b"""\
HTTP/1.1 200 OK
Content-Length: 0
Date: Sat, 05 Jun 2021 22:56:51 GMT
X-CSRF-Token: d637346c70aef677458de33c363104dc71e71133b2b0ff999206ec439d3c2b5f

"""
    parser = python_http_parser.stream.HTTPParser(is_response=True)

    attach_common_event_handlers(parser, results, errors, True)
    parser.process(msg)

    assert len(errors) == 0
    assert parser.finished()
    assert results['http_version'] == (1, 1)
    assert results['status_code'] == 200
    assert results['reason'] == 'OK'
    assert len(results['raw_headers']) == 6


def test_res_no_reason():
    """
    Test the event-based parser with a HTTP response that does not have a reason phrase.
    """
    errors = []
    results = {
        'reason': None,
        'status_code': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b"""\
HTTP/1.1 200
Vary: Accept-Language
Cache-Control: max-age=900
Date: Sat, 05 Jun 2021 22:56:51 GMT

"""

    parser = python_http_parser.stream.HTTPParser(is_response=True)

    attach_common_event_handlers(parser, results, errors, True)
    parser.process(msg)

    assert len(errors) == 0
    assert parser.finished()
    assert results['http_version'] == (1, 1)
    assert results['status_code'] == 200
    assert results['reason'] == ''
    assert len(results['raw_headers']) == 6

def test_chunked_res():
    """
    Test the stream/event based parser with a HTTP response that doesn't arrive
    at once.
    """
    errors = []
    results = {
        'reason': None,
        'status_code': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b''.join([
        b'HTTP/1.1 200 OK\r\n',
        b'Cache-Control: no-cache\r\n',
        b"Content-Security-Policy: default-src 'none'\r\n",
        b'Date: Sat, 05 Jun 2021 22:56:51 GMT\r\n\r\n'
    ])
    parser = python_http_parser.stream.HTTPParser(is_response=True)

    attach_common_event_handlers(parser, results, errors, True)
    parser_process_chunks(parser, chunk(msg, 4))

    assert len(errors) == 0
    assert parser.finished()
    assert results['http_version'] == (1, 1)
    assert results['status_code'] == 200
    assert results['reason'] == 'OK'
    assert len(results['raw_headers']) == 6

def test_reset():
    """
    Make sure the stream/event based parser could reset itself.
    """
    errors = []
    result = {
        'reason': None,
        'status_code': None,
        'req_uri': None,
        'http_version': None,
        'headers': {},
        'raw_headers': []
    }
    msg = b''.join([
        b'HTTP/1.1 200 OK\r\n',
        b'Cache-Control: no-cache\r\n',
        b"Content-Security-Policy: default-src 'none'\r\n",
        b'Date: Sat, 05 Jun 2021 22:56:51 GMT\r\n\r\n'
    ])
    parser = python_http_parser.stream.HTTPParser(is_response=True)
    attach_common_event_handlers(parser, result, errors, True)
    parser.process(msg)

    assert parser.finished()
    assert len(errors) == 0

    # Reset...
    parser.reset()

    assert not parser.finished()
    assert len(errors) == 0

    # Parse again :D
    parser.process(msg)

    assert parser.finished()
    assert len(errors) == 0
