"""Make sure the ``parse()`` function fails when it's supposed to.

This file houses tests to make sure that the ``parse()`` function does
fail when it's supposed to.
"""

# We don't care about catching too-general exceptions.
# pylint: disable=W0703

from .context import python_http_parser


def test_fail_lf_linebreaks():
    """Make sure the parse function raises an error when dealing with LF in strict mode."""
    err = None
    result = None
    msg = 'GET / HTTP/1.1\n' \
        + 'Host: subexample.example.com\n' \
        + 'User-Agent: I_use_::LF.\n\n'

    try:
        result = python_http_parser.parse(msg, strictness_level=3)
    except Exception as ex:
        err = ex

    assert err is not None and isinstance(err,
        python_http_parser.errors.NewlineError)
    assert result is None


def test_fail_empty_header():
    """
    Make sure the parse function raises an error when dealing with empty headers in strict mode.
    """
    err = None
    result = None
    msg = 'HTTP/1.1 400 Bad Request\r\n' \
        + 'A:\r\n' \
        + 'Connection: close\r\n\r\n'

    try:
        result = python_http_parser.parse(
            msg, strictness_level=3, is_response=True)
    except Exception as ex:
        err = ex

    assert err is not None and isinstance(
        err, python_http_parser.errors.LengthError)
    assert result is None


def test_fail_whitespace_before_header():
    """
    Make sure the parse function raises an error when dealing
    with whitespace before headers when not in lenient mode.
    """
    err = None
    result = None
    msg = """\
POST /form HTTP/1.1
  X-Invalid: 1

    """

    try:
        result = python_http_parser.parse(msg)
    except Exception as ex:
        err = ex

    assert err is not None and isinstance(
        err, python_http_parser.errors.ParsingError)
    assert result is None

def test_fail_double_newline():
    """Make sure the parse function raises an error when it can't find a double newline."""
    err = None
    result = None
    msg = """\
HTTP/1.1 200 Not OK
X-Invalid: 1
X-Missing-Double-Newline: 1
    """

    try:
        result = python_http_parser.parse(msg, is_response=True)
    except Exception as ex:
        err = ex

    assert err is not None and isinstance(
        err, python_http_parser.errors.NewlineError)
    assert result is None
