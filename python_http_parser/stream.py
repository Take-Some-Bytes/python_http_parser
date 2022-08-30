"""
The ``python_http_parser.stream`` module provides a HTTP parser that
plays nicer with streams of data, which do not arrive all at once.
"""

__all__ = [
    'HTTPParser'
]

import string
from typing import Union, Optional, NamedTuple

from . import body, constants, errors
from .constants import ParserState, ParserStrictness
from .helpers.events import EventEmitter
from .helpers.newline import find_newline, startswith_newline, NewlineType

_DIGITS = tuple(string.digits.encode('utf-8'))
_HTTP_VER_START = b'HTTP/1.'
_SPACE = 0x20
_COLON = 0x3a


class HTTPVersion(NamedTuple):
    """Represents a HTTP version."""
    major: int
    minor: int


class _ParseResult(NamedTuple):
    data: bytes
    nprocessed: int


class _ProcessResult(NamedTuple):
    nprocessed: int
    remaining: bytes


class HTTPParser(EventEmitter):
    """An event-based push parser for HTTP messages."""

    def __init__(self, strictness: ParserStrictness = ParserStrictness.NORMAL,
                 is_response: bool = False) -> None:
        """Create a new HTTPParser.

        A HTTPParser object provides an incremental, event-based API for parsing
        HTTP messages. The parsed message is pushed to the caller via synchronous
        events.
        """
        super().__init__()
        self.strictness = strictness
        self.is_response = is_response

        self._has_body = False
        self._body_processor: Optional[body.BodyProcessor] = None
        self._state = ParserState.EMPTY

    def _error(self, err: Exception) -> None:
        """Raise or emit an Exception."""
        self._state = ParserState.HAD_ERROR

        if len(self.listeners('error')) < 1:
            # Unhandled exception.
            raise err

        self.emit('error', err)

    def _setup_body_processor(self):
        """Set up this HTTPParser's body processor."""
        def on_data(chunk):
            self.emit('data', chunk)

        def on_error(err):
            self._error(err)

        def on_finished():
            self._state = ParserState.DONE

        self._body_processor.on_data(on_data)
        self._body_processor.on_error(on_error)
        self._body_processor.on_finished(on_finished)

    def _process_request_line(self, buf: bytes) -> _ProcessResult:
        """Process the HTTP request line, which is in ``buf``.

        Internal method. All errors will be propagated back to the caller.
        """
        # We don't really care about too many local variables.
        # pylint: disable=R0914
        nprocessed = 0
        allow_lf = self.strictness != ParserStrictness.STRICT

        if self._state is ParserState.RECEIVING_METHOD:
            m_result = _recv_method(buf)
            if m_result is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            method, nrecved = m_result
            nprocessed += nrecved
            buf = buf[nrecved:]

            self.emit('req_method', method)
            self._state = ParserState.RECEIVING_URI

        if self._state is ParserState.RECEIVING_URI:
            u_result = _recv_uri(buf)
            if u_result is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            uri, nrecved = u_result
            nprocessed += nrecved
            buf = buf[nrecved:]

            self.emit('req_uri', uri)
            self._state = ParserState.PARSING_VERSION

        if self._state is ParserState.PARSING_VERSION:
            version = _parse_version(buf)
            if version is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            # It's always eight bytes
            buf = buf[8:]

            # There must be a newline after this.
            n_result = startswith_newline(buf, allow_lf)
            if n_result is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            is_newline, newline_type = n_result
            if not is_newline:
                raise errors.InvalidVersion(
                    'Expected newline after version!')

            newline_len = 2 if newline_type is NewlineType.CRLF else 1
            buf = buf[newline_len:]
            nprocessed += newline_len

            # We parsed 8 bytes from the HTTP version.
            nprocessed += 8

            self.emit('version', version)
            self._state = ParserState.DONE_STARTLINE

        return _ProcessResult(nprocessed, buf)

    def _process_status_line(self, buf: bytes) -> _ProcessResult:
        """Process the HTTP status line which is in ``buf``.

        Internal method. All errors will be propagated back to the caller.
        """
        # We don't care about that here either.
        # pylint: disable=R0914,R0911
        nprocessed = 0
        allow_lf = self.strictness != ParserStrictness.STRICT

        if self._state is ParserState.PARSING_VERSION:
            version = _parse_version(buf)
            if version is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            buf = buf[8:]

            # Check that there is a space.
            is_space = buf.startswith(b' ')
            if not is_space:
                if len(buf) > 0:
                    # You should have a space.
                    raise errors.UnexpectedChar(
                        f'Expected space after version, received {chr(buf[0])}.')
                # Otherwise, it's incomplete.
                return _ProcessResult(nprocessed, buf)

            # Process the space.
            nprocessed += 1
            buf = buf[1:]

            # We parsed 8 bytes.
            nprocessed += 8

            self.emit('version', version)
            self._state = ParserState.RECEIVING_STATUS_CODE

        if self._state is ParserState.RECEIVING_STATUS_CODE:
            status_code = _recv_code(buf)
            if status_code is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            # +3 because of 3-digit status code.
            nprocessed += 3
            buf = buf[3:]

            self.emit('status_code', status_code)
            self._state = ParserState.RECEIVING_REASON

        if self._state is ParserState.RECEIVING_REASON:
            # If a newline is received directly after the status code and the
            # parser strictness isn't ParserStrictness.STRICT, treat the reason
            # phrase as non-existent.
            n_result = startswith_newline(buf, allow_lf)
            if n_result is None:
                return _ProcessResult(nprocessed, buf)

            is_newline, newline_type = n_result
            if is_newline:
                # Reason phrase doesn't exist.
                # Oh well
                newline_len = 2 if newline_type is NewlineType.CRLF else 1
                nprocessed += newline_len
                buf = buf[newline_len:]

                self.emit('reason', b'')
                self._state = ParserState.DONE_STARTLINE
                return _ProcessResult(nprocessed, buf)

            # We have a reason phrase.
            # Check that there is a space.
            is_space = buf.startswith(b' ')
            if not is_space:
                if len(buf) > 0:
                    # You should have a space.
                    raise errors.UnexpectedChar(
                        f'Expected space before reason phrase, got {chr(buf[0])}.')
                # Otherwise, it's incomplete.
                return _ProcessResult(nprocessed, buf)

            # Process the space.
            # Don't increment nparsed because we'll need the space again
            # if the reason phrase is incomplete.
            buf = buf[1:]

            r_result = _recv_reason(buf, allow_lf)
            if r_result is None:
                # Incomplete.
                return _ProcessResult(nprocessed, buf)

            reason, reason_len = r_result
            # +1 because we need to account for the space.
            nprocessed += reason_len + 1
            buf = buf[reason_len:]

            self.emit('reason', reason)
            self._state = ParserState.DONE_STARTLINE

        return _ProcessResult(nprocessed, buf)

    def _process_headers(self, buf: bytes) -> _ProcessResult:
        """Process the HTTP headers.

        Internal method. All errors will be propagated back to the caller.
        This method assumes that a newline has alread been received before
        the headers start.
        """
        nprocessed = 0
        allow_lf = self.strictness != ParserStrictness.STRICT
        headers_over = False
        while not headers_over:
            if self._state is ParserState.PARSING_HEADER_NAME:
                n_result = startswith_newline(buf, allow_lf)
                if n_result is None:
                    break

                is_newline, newline_type = n_result
                if is_newline:
                    # Headers are over!
                    newline_len = 2 if newline_type is NewlineType.CRLF else 1
                    nprocessed += newline_len
                    buf = buf[newline_len:]
                    headers_over = True
                    break

                # Here comes another header name!
                hn_result = _recv_header_name(buf)
                if hn_result is None:
                    # Incomplete.
                    break
                header_name, nrecved = hn_result
                nprocessed += nrecved
                buf = buf[nrecved:]

                self.emit('header_name', header_name)
                self._state = ParserState.PARSING_HEADER_VAL

            if self._state is ParserState.PARSING_HEADER_VAL:
                hv_result = _recv_header_value(buf, allow_lf)
                if hv_result is None:
                    # Incomplete.
                    break
                header_val, nrecved = hv_result
                nprocessed += nrecved
                buf = buf[nrecved:]

                self.emit('header_value', header_val)
                self._state = ParserState.PARSING_HEADER_NAME

        if headers_over:
            self.emit('headers_complete')
            self._state = ParserState.DONE_HEADERS

        return _ProcessResult(nprocessed, buf)

    def _process(self, buf: bytes) -> int:
        """Internal ``._process()`` method.

        Contains the parser directing logic. All errors will be propagated
        back to the caller.
        """
        # pylint: disable=R0912

        nparsed = 0
        if self.is_response and self._state in (
                ParserState.PARSING_VERSION,
                ParserState.RECEIVING_STATUS_CODE,
                ParserState.RECEIVING_REASON):
            (nprocessed, buf) = self._process_status_line(buf)
            nparsed += nprocessed
        elif self._state in (
            ParserState.RECEIVING_METHOD,
            ParserState.RECEIVING_URI,
            ParserState.PARSING_VERSION
        ):
            (nprocessed, buf) = self._process_request_line(buf)
            nparsed += nprocessed

        if self._state is ParserState.DONE_STARTLINE:
            self.emit('startline_complete')
            self._state = ParserState.PARSING_HEADER_NAME

        if self._state in (
            ParserState.PARSING_HEADER_NAME,
            ParserState.PARSING_HEADER_VAL
        ):
            (nprocessed, buf) = self._process_headers(buf)
            nparsed += nprocessed

        if self._state is ParserState.DONE_HEADERS:
            if self._has_body:
                if self._body_processor is None:
                    raise errors.BodyProcessorRequired()

                self._state = ParserState.PROCESSING_BODY
                self._setup_body_processor()
            else:
                self._state = ParserState.DONE

        if self._state is ParserState.PROCESSING_BODY:
            if self._body_processor is None:
                raise errors.BodyProcessorRequired()

            ret = self._body_processor.process(
                buf, self.strictness != ParserStrictness.STRICT
            )
            if ret < 0:
                # Error!
                nparsed = -1
            else:
                nparsed += ret

        if self._state is ParserState.DONE:
            self.emit('message_complete')

        return nparsed

    def has_body(
        self, has_body: bool = None
    ) -> bool:
        """Get or set whether this parser should expect a body."""
        if has_body is not None:
            self._has_body = has_body
        return self._has_body

    def body_processor(
        self, body_processor: body.BodyProcessor = None
    ) -> Optional[body.BodyProcessor]:
        """Get or set the body processor this parser is going to use."""
        if body_processor is not None:
            self._body_processor = body_processor
        return self._body_processor

    def finished(self) -> bool:
        """Return ``True`` if this parser is finished."""
        return self._state is ParserState.DONE

    def reset(self) -> None:
        """Reset the parser state."""
        self._has_body = False
        self._body_processor = None
        self._state = ParserState.EMPTY

    def process(self, data: Union[bytes, bytearray, memoryview]) -> int:
        """Process the contents of ``data`` as part of the HTTP message.

        Returns the number of bytes processed. Any unprocessed bytes must
        be buffered for the next call to ``parser.process()``.

        The integer ``-1`` means that an error was encountered during parsing,
        and thus parsing should stop.
        """
        if self._state is ParserState.DONE:
            self._error(errors.DoneError())

        if self._state is ParserState.HAD_ERROR:
            # We has error.
            return -1

        # Copy it, then we could get started.
        buf = bytes(data)

        try:
            nskipped = 0

            if self._state is ParserState.EMPTY:
                # Only try to skip empty lines if this parser is in request mode.
                if self.is_response:
                    self._state = ParserState.PARSING_VERSION
                else:
                    ret = _skip_empty_lines(
                        buf, self.strictness != ParserStrictness.STRICT)
                    if ret is None:
                        # Message is not complete,
                        # but we still processed all of it.
                        return len(buf)
                    self._state = ParserState.RECEIVING_METHOD

                    nskipped += ret

                    buf = buf[nskipped:]

            return self._process(buf) + nskipped
        except (errors.InvalidVersion, errors.NewlineError,
                errors.UnexpectedChar, errors.InvalidStatus,
                errors.InvalidToken, errors.InvalidURI,
                errors.InvalidHeaderVal, errors.BodyProcessorRequired) as ex:
            self._error(ex)
            return -1


def _skip_empty_lines(
    buf: bytes,
    allow_lf: bool
) -> Optional[int]:
    """Skip all empty lines."""
    pos = 0

    while True:
        is_cr = buf.startswith(b'\r', pos)
        if is_cr:
            if not buf.startswith(b'\r\n', pos):
                # Bare CR!
                raise errors.NewlineError('Expected CRLF, received bare CR.')

            pos += 2
            continue

        is_lf = buf.startswith(b'\n', pos)
        if is_lf:
            if not allow_lf:
                # Oops! LF isn't allowed.
                raise errors.NewlineError('CRLF is required!')

            pos += 1
            continue

        # It's not LF and it's not CRLF, so it could
        # either be empty or we actually have data.
        break

    if len(buf) - pos > 0:
        # We have data!
        return pos

    # No data
    return None


def _parse_version(buf: bytes) -> Optional[HTTPVersion]:
    """Parse the HTTP version that exists in ``buf``."""
    if len(buf) < 8:
        # Too short.
        return None

    next_8 = buf[:8]

    if not next_8.startswith(_HTTP_VER_START):
        raise errors.InvalidVersion(
            f'Expected HTTP version start, received {next_8[:7]!r}')

    # It's time for the last byte.
    # We only accept 0 (HTTP/1.0) and 1 (HTTP/1.1).
    last_byte = next_8[7]
    if last_byte not in (_DIGITS[0], _DIGITS[1]):
        raise errors.InvalidVersion(
            f'Expected 0 or 1 for HTTP minor version, received {bytes([last_byte])!r}'
        )

    return HTTPVersion(1, int(bytes([last_byte])))


def _recv_method(buf: bytes) -> Optional[_ParseResult]:
    """Receive the HTTP request method in ``buf``.

    Returns a tuple containing the request method and the number of bytes parsed.
    """
    nrecved = 0
    space_index = buf.find(_SPACE)
    if space_index < 0:
        # Before assuming it is incomplete, we have to check something.
        if len(buf) > constants.MAX_REQ_METHOD_LEN:
            # There are way too many bytes.
            raise errors.InvalidToken('Request method too large!')
        # Now we know it's incomplete.
        return None

    # The token needs to actually exist.
    if space_index == 0:
        raise errors.InvalidToken(
            'Expected token in HTTP method, received space.')
    if space_index > constants.MAX_REQ_METHOD_LEN:
        raise errors.InvalidToken('Request method too large!')

    # +1 because of the space
    nrecved += space_index + 1
    method = buf[:space_index]

    if not _is_token(method):
        raise errors.InvalidToken('Expected token in HTTP method')

    return _ParseResult(method, nrecved)


def _recv_uri(buf: bytes) -> Optional[_ParseResult]:
    """Receive the HTTP request URI in ``buf``.

    Returns a tuple containing the request URI and number of bytes
    consumed. No parsing of the URI is done.
    """
    nrecved = 0
    space_index = buf.find(_SPACE)
    if space_index < 0:
        # Before assuming it is incomplete, we have to check something.
        if len(buf) > constants.MAX_URI_LEN:
            # There are way too many bytes.
            raise errors.InvalidURI('Request URI too large!')
        # Incomplete URI.
        return None

    # Please actually include an URI.
    if space_index == 0:
        raise errors.InvalidURI('Expected URI character, received space.')
    if space_index > constants.MAX_URI_LEN:
        raise errors.InvalidURI('Request URI too large!')

    # +1 because of the space.
    nrecved = space_index + 1
    uri = buf[:space_index]

    if not _is_uri(uri):
        raise errors.InvalidURI(
            'Expected URI characters in HTTP URI.')

    return _ParseResult(uri, nrecved)


def _recv_code(buf: bytes) -> Optional[int]:
    """Receive the HTTP status code in ``buf``."""
    if len(buf) < 3:
        # Not enough bytes.
        return None

    raw_code = buf[:3]
    if not _are_digits(raw_code):
        raise errors.InvalidStatus('Expected only digits in status code!')

    return int(raw_code)


def _recv_reason(buf: bytes, allow_lf: bool) -> Optional[_ParseResult]:
    """Receive the HTTP reason phrase.

    This function assumes that the reason phrase exists, so if you wish
    to make the reason phrase optional, you must check for its existence
    yourself.

    This function will "eat" (i.e. ignore and drop) any whitespace that appears
    at the start and end of the reason phrase.

    Returns the reason phrase and an integer representing the number of
    bytes parsed.
    """
    nrecved = 0

    newline_idx, newline_type = find_newline(buf, allow_lf)
    if not bool(~newline_idx):
        # Hmmm...
        if len(buf) > constants.MAX_REASON_LEN:
            # There should be a newline, since there are many more
            # characters than the maximum allowed in a reason phrase.
            raise errors.InvalidStatus('Reason phrase too large!')
        # Otherwise, it's incomplete.
        return None
    if newline_idx > constants.MAX_REASON_LEN:
        raise errors.InvalidStatus('Reason phrase too large!')

    nrecved += newline_idx
    nrecved += 2 if newline_type is NewlineType.CRLF else 1
    reason = buf[:newline_idx].strip()

    if not _is_vchar_or_whsp(reason):
        # Check for obsolete text.
        if not _is_obs_text(
                reason.translate(None, constants.VCHAR_OR_WSP)):
            raise errors.InvalidStatus(
                'Invalid characters in response reason phrase!')
        # We has obsolete text.
        return _ParseResult(b'', nrecved)

    return _ParseResult(reason, nrecved)


def _recv_header_name(buf: bytes) -> Optional[_ParseResult]:
    """Receive a HTTP header field name from ``buf``.

    This method does NOT treat newlines (``\\n`` or ``\\r\\n``) as the end
    of HTTP headers. That means, any newlines will be handled as if they were
    invalid header characters. You must check for newlines yourself.
    """
    nrecved = 0
    colon_index = buf.find(_COLON)

    if colon_index < 0:
        # If there are more characters in the data than the maximum allowed
        # characters in a header name, then something's wrong.
        if len(buf) > constants.MAX_HEADER_NAME_LEN:
            raise errors.InvalidToken('Header name too long!')
        # Otherwise, it's incomplete.
        return None

    if colon_index == 0:
        # Tokens must be at least 1 char long. Header names are tokens.
        raise errors.InvalidToken('Tokens must be at least one char long.')
    if colon_index > constants.MAX_HEADER_NAME_LEN:
        raise errors.InvalidToken('Header name too long!')

    # +1 because of the colon.
    nrecved += colon_index + 1
    header_name = buf[:colon_index]

    if not _is_token(header_name):
        raise errors.InvalidToken(
            'Invalid characters in header name!')

    return _ParseResult(header_name, nrecved)


def _recv_header_value(buf: bytes, allow_lf: bool) -> Optional[_ParseResult]:
    """Receive a HTTP header field value from ``buf``.

    This function will "eat" (i.e. ignore and drop) any whitespace that appears
    before any other characters in the field value.
    """
    nrecved = 0
    newline_idx, newline_type = find_newline(buf, allow_lf)
    if not bool(~newline_idx):
        # Hmmm...
        if len(buf) > constants.MAX_HEADER_VAL_SIZE:
            # There should be a newline, since there are many more
            # characters than the maximum allowed in a header value.
            raise errors.InvalidHeaderVal('Header field value too large!')
        # Otherwise, it's incomplete.
        return None
    if newline_idx > constants.MAX_HEADER_VAL_SIZE:
        raise errors.InvalidHeaderVal('Header field value too large!')

    nrecved += newline_idx
    nrecved += 2 if newline_type is NewlineType.CRLF else 1
    header_val = buf[:newline_idx].strip()

    if not _is_vchar_or_whsp(header_val):
        # Check for obsolete text.
        if not _is_obs_text(
                header_val.translate(None, constants.VCHAR_OR_WSP)):
            raise errors.InvalidHeaderVal(
                'Invalid characters in header value!')

        # We has obsolete text.
        return _ParseResult(b'', nrecved)

    return _ParseResult(header_val, nrecved)


def _is_token(_bytes: bytes) -> bool:
    """Are the bytes a valid HTTP token?"""
    # Delete all valid characters. Any characters left are invalid.
    return len(_bytes.translate(None, constants.TOKENS)) == 0


def _is_uri(_bytes: bytes) -> bool:
    """Could the bytes be a valid URI? (i.e. do the bytes have valid URI chars)."""
    # Delete all valid characters. Any characters left are invalid.
    return len(_bytes.translate(None, constants.URI_CHARS)) == 0


def _is_vchar_or_whsp(_bytes: bytes) -> bool:
    """Do the bytes only contain VCHARs and whitespace?"""
    return len(_bytes.translate(None, constants.VCHAR_OR_WSP)) == 0


def _is_obs_text(_bytes: bytes) -> bool:
    """Do the bytes only contain obsolete text?"""
    return len(_bytes.translate(None, constants.OBS_TXT)) == 0


def _are_digits(_bytes: bytes) -> bool:
    """Do the bytes only contain numerical characters?"""
    return len(_bytes.translate(None, constants.DIGITS)) == 0
