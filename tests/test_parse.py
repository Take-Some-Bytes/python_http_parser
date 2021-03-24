"""Testing the ``parse()`` function.

This file houses tests for the basic ``parse()`` function, which take a
string, bytes, or bytearray and treats it as a somewhat complete HTTP
message, and parses it.
"""

# We don't care about catching too-general exceptions.
# pylint: disable=W0703

from .context import python_http_parser


def test_parser_rfc7230_req():
    """Test the parser with HTTP requests that conform to RFC7230."""
    errors = []
    results = []
    messages = [
        """\
GET /index.html HTTP/1.1
Host: example.org
Accept: text/html, text/*, */*
User-Agent: TESTINGTESTING/123
X-Test-Header: FOOO:::FOOO

        """,
        """\
POST /form-submission?that=this HTTP/1.1
Host: example.org
Content-Type: text/plain
User-Agent: 100:Reqs:Per:Day
Content-Length: 28

I want to believe!!!!!!!!!!!
        """
    ]

    for msg in messages:
        try:
            results.append(python_http_parser.parse(msg))
        except Exception as ex:
            errors.append(ex)

    # None of the parse calls should have raised an exception.
    assert len(errors) == 0
    assert len(results) == 2

    for result in results:
        assert result['status_code'] is None
        assert result['status_msg'] is None
        assert result['req_method'] is not None and isinstance(
            result['req_method'], str)
        assert result['req_uri'] is not None and isinstance(
            result['req_uri'], str)
        assert result['http_ver'] is not None and result['http_ver'] == 1.1
        assert (result['headers'] is not None) and (
            isinstance(result['headers'], dict)) and (len(result['headers']) == 4)
        assert result['raw_headers'] is not None and isinstance(
            result['raw_headers'], list)
        assert result['body'] is None or isinstance(result['body'], str)


def test_parser_rfc7230_res():
    """Test the parser with HTTP responses that conform to RFC7230."""
    errors = []
    results = []
    messages = [
        """\
HTTP/1.1 404 D3F1N173LY N07 F0UND
Connection: close
Content-Type: text/plain
Content-Length: 63
Retry-After: 160000
X-Test-Header: FOOO:::FOOO

7H3 R350URC3 R3QU3573D W45 D3F1N173LY N07 F0UND 0N 7H15 53RV3R.
        """,
        """\
HTTP/1.1 401 Unauthenticated
Connection: close
Content-Type: text/plain
Content-Length: 56
Retry-After: 160000
WWW-Authenticate: Basic realm="Access to the staging site", charset="UTF-8"

Please authenticate yourself to access the staging site.
        """
    ]

    for msg in messages:
        try:
            results.append(python_http_parser.parse(msg, is_response=True))
        except Exception as ex:
            errors.append(ex)

    # None of the parse calls should have raised an exception.
    assert len(errors) == 0
    assert len(results) == 2

    for result in results:
        assert isinstance(result['status_code'], int) and result['status_code'] > 400
        assert isinstance(result['status_msg'], str)
        assert result['req_method'] is None
        assert result['req_uri'] is None
        assert result['http_ver'] is not None and result['http_ver'] == 1.1
        assert (result['headers'] is not None) and (
            isinstance(result['headers'], dict)) and (len(result['headers']) == 5)
        assert result['raw_headers'] is not None and isinstance(
            result['raw_headers'], list)
        assert isinstance(result['body'], str)


def test_parser_with_duplicate():
    """Test the parser with a duplicate header."""
    error = None
    result = None
    msg = """\
GET / HTTP/1.1
Cookie: this=that
Cookie: duplicate=1
Host: sub2.example.com

        """

    try:
        result = python_http_parser.parse(msg)
    except Exception as ex:
        error = ex

    assert error is None
    assert result is not None
    assert isinstance(result['headers']['cookie'], list)


def test_parser_alias():
    """Test the alias of the parse function."""
    error = None
    result = None
    msg = """\
POST /form-submission?that=this HTTP/1.1
Host: example.org
Content-Type: text/plain
User-Agent: 100:Reqs:Per:Day
Content-Length: 28

I want to believe!!!!!!!!!!!
        """

    try:
        result = python_http_parser.decode(msg)
    except Exception as ex:
        error = ex

    assert error is None
    assert result is not None
    assert result['status_code'] is None
    assert result['status_msg'] is None
    assert result['req_method'] is not None and isinstance(
        result['req_method'], str)
    assert result['req_uri'] is not None and isinstance(result['req_uri'], str)
    assert result['http_ver'] is not None and result['http_ver'] == 1.1
    assert (result['headers'] is not None) and (
        isinstance(result['headers'], dict)) and (len(result['headers']) == 4)
    assert result['raw_headers'] is not None and isinstance(
        result['raw_headers'], list)
    assert result['body'] is None or isinstance(result['body'], str)
