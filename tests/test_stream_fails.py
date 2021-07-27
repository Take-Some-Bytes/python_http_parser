"""
Tests for the ``python_http_parser.stream.HTTPParser`` class that
requires it to fail.
"""

from .context import python_http_parser


def test_fail_inval_ver():
    """The HTTPParser class should emit an error if HTTP version is invalid."""
    errors = []
    msgs = [
        b'GET /index.html IHOP/1.3\r\n\r\n',
        b'POST /index.html HTTP/1.9\n\n',
        b'HYTP\\1.1 500 Invalid\r\n\r\n',
        b'HTTP/0.1 200 Definitely OK\n\n'
    ]
    index = 0

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        if index > 1:
            # It's time for response parsing.
            parser = python_http_parser.stream.HTTPParser(is_response=True)
        else:
            parser = python_http_parser.stream.HTTPParser()

        parser.on('error', on_error)
        parser.process(msg)
        index += 1

    assert len(errors) == 4
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.InvalidVersion),
        errors
    ))


def test_fail_bare_cr():
    """The HTTPParser class should not accept bare CR."""
    errors = []
    msgs = [
        b'GET /index.html HTTP/1.1\r\r',
        b'HTTP/1.1 500 Not correct\r\r'
    ]
    index = 0

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        if index > 0:
            # Response parsing!
            # It's time for response parsing.
            parser = python_http_parser.stream.HTTPParser(is_response=True)
        else:
            parser = python_http_parser.stream.HTTPParser()

        parser.on('error', on_error)
        parser.process(msg)
        index += 1

    assert len(errors) == 2
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.NewlineError),
        errors
    ))


def test_fail_unexpected_char():
    """
    The HTTPParser class should raise UnexpectedChar when an unexpected character appears.
    """
    errors = []
    msgs = [
        # In both of these, a space is required but not received.
        b'HTTP/1.1200 NOPE',
        b'HTTP/1.1 200STILLNOPE'
    ]

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        parser = python_http_parser.stream.HTTPParser(is_response=True)
        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) == 2
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.UnexpectedChar),
        errors
    ))


def test_fail_inval_status():
    """
    The HTTPParser class should reject status lines with invalid
    status codes and invalid characters in reason phrase.
    """
    errors = []
    msgs = [
        # There's an "o" in the 200.
        b'HTTP/1.1 2O0 OK\r\n',
        # No null bytes!
        b'HTTP/1.1 200 \x00K\r\n'
    ]

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        parser = python_http_parser.stream.HTTPParser(is_response=True)
        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) == 2
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.InvalidStatus),
        errors
    ))


def test_fail_inval_token():
    """The HTTPParser should reject HTTP messages with invalid tokens."""
    errors = []
    msgs = [
        b'G@T / HTTP/1.1',
        # Extra spaces aren't allowed!
        b' GET / HTTP/1.1'
    ]

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        parser = python_http_parser.stream.HTTPParser()
        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) == 2
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.InvalidToken),
        errors
    ))


def test_fail_inval_uri_char():
    """The HTTPParser should reject HTTP requests with invalid URI characters."""
    errors = []
    msgs = [
        # Backslashes ("\") aren't allowed.
        b'GET /\\ HTTP/1.1',
        # Again, extra spaces aren't allowed.
        b'GET  / HTTP/1.1'
    ]

    def on_error(err):
        errors.append(err)

    for msg in msgs:
        parser = python_http_parser.stream.HTTPParser()
        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) == 2
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.InvalidURI),
        errors
    ))


def test_fail_extra_newline_res():
    """
    Make sure the parser fails when there are extra newlines at
    the start of a HTTP response.
    """
    errors = []
    msg = b'\r\n\r\nHTTP/1.1 500 This Message Is Invalid\r\n\r\n'

    def on_error(err):
        errors.append(err)

    parser = python_http_parser.stream.HTTPParser(is_response=True)
    parser.on('error', on_error)
    parser.process(msg)

    assert len(errors) == 1
    # InvalidVersion error because the parser expects the HTTP version,
    # not a bunch of newlines.
    assert isinstance(errors[0], python_http_parser.errors.InvalidVersion)

def test_invalid_lf_strict():
    """
    Make sure the parser fails if strict mode is on and an LF is encountered.
    """
    errors = []
    msgs = [
        b'HTTP/1.1 200 Inccorect Line Breaks\n\n',
        b'GET /index.html HTTP/1.1\n\n'
    ]
    def on_error(err):
        errors.append(err)

    # Do it once with new parser strictness IntEnum.
    for (i, msg) in enumerate(msgs):
        if i == 0:
            parser = python_http_parser.stream.HTTPParser(
                is_response=True,
                strictness=python_http_parser.constants.ParserStrictness.STRICT
            )
        else:
            parser = python_http_parser.stream.HTTPParser(
                strictness=python_http_parser.constants.ParserStrictness.STRICT
            )

        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) > 0
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.NewlineError),
        errors
    ))

    errors.clear()

    # And another time with old strictness constants.
    for (i, msg) in enumerate(msgs):
        if i == 0:
            parser = python_http_parser.stream.HTTPParser(
                is_response=True,
                strictness=python_http_parser.constants.PARSER_STRICT
            )
        else:
            parser = python_http_parser.stream.HTTPParser(
                strictness=python_http_parser.constants.PARSER_STRICT
            )

        parser.on('error', on_error)
        parser.process(msg)

    assert len(errors) > 0
    assert all(map(
        lambda ex: isinstance(ex, python_http_parser.errors.NewlineError),
        errors
    ))
