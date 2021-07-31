"""
The ``python_http_parser.stream`` module provides a HTTP parser that
plays nicer with streams of data, which do not arrive all at once.
"""

__all__ = [
    'HTTPParser'
]

import string
from collections import namedtuple
from typing import Any, Iterator, Optional, Tuple

from . import body, bytedata, constants, errors
from .constants import ParserState, ParserStrictness
from .helpers.events import EventEmitter
from .helpers.newline import find_newline, is_newline

_DIGITS = tuple(string.digits.encode('utf-8'))
_HTTP_VER_START = b'HTTP/1.'
# Horizontal tab ("\t" in Python).
_SPACE = 0x20
_COLON = 0x3a


HTTPVersion = namedtuple('HTTPVersion', ['major', 'minor'])


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

    def _process_request_line(self, buf: bytedata.Bytes) -> int:
        """Process the HTTP request line, which is in ``buf``.

        Internal method. All errors will be propagated back to the caller.
        """
        nparsed = 0
        allow_lf = self.strictness != ParserStrictness.STRICT

        if self._state is ParserState.RECEIVING_METHOD:
            result = _recv_method(buf)
            if result is None:
                # Incomplete method, so tell caller to buffer everything.
                return nparsed

            method, parsed = result
            nparsed += parsed

            self.emit('req_method_complete')
            self.emit('req_method', method)
            self._state = ParserState.RECEIVING_URI

        if self._state is ParserState.RECEIVING_URI:
            result = _recv_uri(buf)
            if result is None:
                # Incomplete, return.
                return nparsed

            uri, parsed = result
            nparsed += parsed

            self.emit('req_uri_complete')
            self.emit('req_uri', uri)
            self._state = ParserState.PARSING_VERSION

        if self._state is ParserState.PARSING_VERSION:
            version = _parse_version(buf)
            if version is None:
                # Incomplete AGAIN.
                return nparsed
            # Time to check that there is a newline.
            is_crlf = is_newline(buf, b'\r\n')
            if is_crlf is None:
                # Not complete.
                return nparsed
            if not is_crlf:
                is_lf = is_newline(buf, b'\n')
                if is_lf is None:
                    return nparsed
                if not allow_lf:
                    raise errors.NewlineError('CRLF is required!')
                if not is_lf:
                    raise errors.InvalidVersion(
                        'Expected newline after version!')
                # It's LF.
                nparsed += 1
            else:
                # It's CRLF.
                nparsed += 2
            buf.slice()

            # We parsed 8 bytes from the HTTP version.
            nparsed += 8

            self.emit('version_complete')
            self.emit('version', HTTPVersion(*version))
            self._state = ParserState.DONE_STARTLINE

        return nparsed

    def _process_status_line(self, buf: bytedata.Bytes) -> int:
        """Process the HTTP status line which is in ``buf``.

        Internal method. All errors will be propagated back to the caller.
        """
        # It's sad we have to do this, but we have 7 returns here, 1 more than
        # PyLint's limit.
        # pylint: disable=too-many-return-statements
        allow_lf = self.strictness != ParserStrictness.STRICT
        result: Any = None

        nparsed = 0
        if self._state is ParserState.PARSING_VERSION:
            version = _parse_version(buf)
            if version is None:
                # Incomplete version, so we'll have to get the user
                # to buffer all the passed-in bytes.
                return nparsed  # (i.e. 0)

            # We parsed 8 bytes. Increase the nparsed variable, which tracks
            # the number of bytes parsed.
            nparsed += 8

            self.emit('version_complete')
            self.emit('version', HTTPVersion(*version))
            self._state = ParserState.RECEIVING_STATUS_CODE

        if self._state is ParserState.RECEIVING_STATUS_CODE:
            if not _expect(_SPACE, iter(buf)):
                # The status code is not complete.
                return nparsed

            # Remove all the stuff we processed.
            buf.slice()
            status_code = _recv_code(buf)
            if status_code is None:
                # Incomplete, buffer all bytes after ``nparsed``
                return nparsed

            # +4 because of the space.
            nparsed += 4

            self.emit('status_complete')
            self.emit('status_code', status_code)

            self._state = ParserState.RECEIVING_REASON

        if self._state is ParserState.RECEIVING_REASON:
            # If a newline is received directly after the status code and the
            # parser strictness isn't ParserStrictness.STRICT, treat the reason
            # phrase as non-existent.
            result = _has_reason(buf, allow_lf)
            if result is None:
                # Incomplete.
                return nparsed
            has_reason, parsed = result
            nparsed += parsed

            if not has_reason:
                # There is not a reason phrase!
                # ``parsed`` contains the number of bytes the function processed.
                buf.slice()
                self.emit('reason_complete')
                self.emit('reason', '')
                self._state = ParserState.DONE_STARTLINE
                return nparsed

            # A space is required if there is supposed to be a reason phrase.
            if not _expect(_SPACE, iter(buf)):
                # The reason phrase is not complete.
                return nparsed

            # Slice the buffer now to remove the previous character from memory.
            buf.slice()
            result = _recv_reason(buf, allow_lf)
            if result is None:
                return nparsed

            reason, reason_len = result
            # +1 because of the space.
            nparsed += reason_len + 1

            self.emit('reason_complete')
            self.emit('reason', reason)
            self._state = ParserState.DONE_STARTLINE

        return nparsed

    def _process_headers(self, buf: bytedata.Bytes) -> int:
        """Process the HTTP headers.

        Internal method. All errors will be propagated back to the caller.
        This method assumes that a newline has alread been received before
        the headers start.
        """
        nparsed = 0
        allow_lf = self.strictness != ParserStrictness.STRICT
        headers_over = False
        while not headers_over:
            if self._state is ParserState.PARSING_HEADER_NAME:
                is_crlf = is_newline(buf, b'\r\n')
                is_lf = is_newline(buf, b'\n')
                if is_crlf is None and is_lf is None:
                    # The message stops there.
                    break
                if is_lf:
                    if not allow_lf:
                        raise errors.NewlineError('CRLF is required!')
                    # Headers are over!
                    nparsed += 1
                    headers_over = True
                    break
                if is_crlf:
                    # It's CRLF
                    nparsed += 2
                    headers_over = True
                    break

                result = _recv_header_name(buf)
                if result is None:
                    break
                header_name, parsed = result
                nparsed += parsed

                self.emit('header_name_complete')
                self.emit('header_name', header_name)
                self._state = ParserState.PARSING_HEADER_VAL

            if self._state is ParserState.PARSING_HEADER_VAL:
                result = _recv_header_value(buf, allow_lf)
                if result is None:
                    break
                header_val, parsed = result
                nparsed += parsed

                self.emit('header_value_complete')
                self.emit('header_value', header_val)
                self._state = ParserState.PARSING_HEADER_NAME

        if headers_over:
            buf.slice()
            self.emit('headers_complete')
            self._state = ParserState.DONE_HEADERS
        return nparsed

    def _process(self, buf: bytedata.Bytes) -> int:
        """Internal ``._process()`` method.

        Contains the parser directing logic. All errors will be propagated
        back to the caller.
        """
        nparsed = 0
        if self.is_response and self._state in (
                ParserState.PARSING_VERSION,
                ParserState.RECEIVING_STATUS_CODE,
                ParserState.RECEIVING_REASON):
            nparsed += self._process_status_line(buf)
        elif self._state in (
            ParserState.RECEIVING_METHOD,
            ParserState.RECEIVING_URI,
            ParserState.PARSING_VERSION
        ):
            nparsed += self._process_request_line(buf)

        if self._state is ParserState.DONE_STARTLINE:
            self.emit('startline_complete')
            self._state = ParserState.PARSING_HEADER_NAME

        if self._state in (
            ParserState.PARSING_HEADER_NAME,
            ParserState.PARSING_HEADER_VAL
        ):
            nparsed += self._process_headers(buf)

        if self._state is ParserState.DONE_HEADERS:
            if self._has_body:
                self._state = ParserState.PROCESSING_BODY
                self._setup_body_processor()
            else:
                self._state = ParserState.DONE

        if self._state is ParserState.PROCESSING_BODY:
            if self._body_processor is None:
                raise errors.BodyProcessorRequired()

            ret = self._body_processor.process(
                buf.as_bytes(), self.strictness != ParserStrictness.STRICT
            )
            if not bool(~ret):
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

    def process(self, data: bytes) -> int:
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

        buf = bytedata.Bytes(data)

        try:
            if self._state is ParserState.EMPTY:
                if self.is_response:
                    self._state = ParserState.PARSING_VERSION
                else:
                    # Only try to skip empty lines if this parser is in request mode.
                    ret = _skip_empty_lines(
                        buf, self.strictness != ParserStrictness.STRICT)
                    if ret is None:
                        # Message is not complete,
                        # but we still processed all of it.
                        return len(data)
                    self._state = ParserState.RECEIVING_METHOD

            return self._process(buf)
        except (errors.InvalidVersion, errors.NewlineError,
                errors.UnexpectedChar, errors.InvalidStatus,
                errors.InvalidToken, errors.InvalidURI,
                errors.InvalidHeaderVal, errors.BodyProcessorRequired) as ex:
            self._error(ex)
            return -1


def _expect(byte: int, byte_iter: Iterator[int]) -> bool:
    """Expect the next byte of ``iterator`` to be ``byte``.

    Raises errors.UnexpectedChar if bytes do not match. Returns
    False if there were no more elements in the iterator.
    Returns True otherwise.
    """
    next_byte = next(byte_iter, None)
    if next_byte is None:
        return False
    if next_byte != byte:
        raise errors.UnexpectedChar(
            'Expected char "{}", received {}'.format(
                chr(byte), chr(next_byte)
            ))

    return True


def _skip_empty_lines(
        buf: bytedata.Bytes,
        allow_lf: bool
) -> Optional[bytedata.Bytes]:
    """Skip all empty lines."""
    while True:
        is_crlf = is_newline(buf, b'\r\n')
        if is_crlf is None:
            return None
        if not is_crlf:
            is_lf = is_newline(buf, b'\n')
            if is_lf is None:
                return None
            if is_lf:
                if not allow_lf:
                    raise errors.NewlineError('CRLF is required!')
                continue
        else:
            continue

        # Finally! A line with stuff in it!
        buf.slice()
        return buf


def _parse_version(buf: bytedata.Bytes) -> Optional[Tuple[int, int]]:
    """Parse the HTTP version that exists in ``buf``."""
    next_8 = buf.next_8()
    if next_8 is None:
        # Incomplete.
        return None

    if not next_8.startswith(_HTTP_VER_START):
        raise errors.InvalidVersion(
            'Expected HTTP version start, received {!r}'.format(
                next_8[:7]
            ))

    # It's time for the last byte.
    # We only accept 0 (HTTP/1.0) and 1 (HTTP/1.1).
    last_byte = next_8[7]

    if last_byte not in (_DIGITS[0], _DIGITS[1]):
        raise errors.InvalidVersion(
            'Expected 0 or 1 for HTTP minor version, received {!r}'.format(
                bytes([last_byte])
            ))

    return (1, int(bytes([last_byte])))


def _has_reason(buf: bytedata.Bytes, allow_lf: bool) -> Optional[Tuple[bool, int]]:
    """Is a reason phrase expected?

    Return None if incomplete. Return a boolean representing whether a reason
    phrase is expected and the number of bytes parsed otherwise.
    """
    nparsed = 0
    is_crlf = is_newline(buf, b'\r\n')
    if is_crlf is None:
        # Not complete.
        return None
    if not is_crlf:
        is_lf = is_newline(buf, b'\n')
        if is_lf is None:
            return None
        if is_lf:
            if not allow_lf:
                raise errors.NewlineError('CRLF is required!')
            has_reason = False
            nparsed += 1
        else:
            # There is no newline, so there is a reason phrase.
            has_reason = True
    else:
        has_reason = False

    return (has_reason, nparsed)


def _recv_uri(buf: bytedata.Bytes) -> Optional[Tuple[str, int]]:
    """Receive the HTTP request URI in ``buf``.

    Returns a tuple containing the request URI and number of bytes
    consumed. No parsing of the URI is done.
    """
    nparsed = 0
    space_index = buf.find(_SPACE)
    if not bool(~space_index):
        # Before assuming it is incomplete, we have to check something.
        if len(buf) > constants.MAX_URI_LEN:
            # There are way too many bytes.
            raise errors.InvalidToken('Request method too large!')
        # Incomplete URI.
        return None
    if space_index < 1:
        raise errors.InvalidURI('Expected URI character, received space.')

    # +1 because of the space.
    nparsed = space_index + 1
    if nparsed > constants.MAX_URI_LEN:
        raise errors.InvalidURI(
            'Exceeded max URI method length of {}'.format(constants.MAX_URI_LEN))

    # +1 to consume the space as well
    buf.advance(space_index + 1)
    # And here, we ignore the space.
    raw_uri = bytes(buf.slice()).strip()

    if not _is_uri(raw_uri):
        raise errors.InvalidURI(
            'Expected URI characters in HTTP URI.')

    uri = raw_uri.decode('utf-8')
    return (uri, nparsed)


def _recv_method(buf: bytedata.Bytes) -> Optional[Tuple[str, int]]:
    """Receive the HTTP request method in ``buf``.

    Returns a tuple containing the request method and the number of bytes parsed.
    """
    nparsed = 0
    space_index = buf.find(_SPACE)
    if not bool(~space_index):
        # Before assuming it is incomplete, we have to check something.
        if len(buf) > constants.MAX_REQ_METHOD_LEN:
            # There are way too many bytes.
            raise errors.InvalidToken('Request method too large!')
        # Incomplete method.
        return None
    if space_index < 1:
        raise errors.InvalidToken(
            'Expected token in HTTP method, received space.')
    # +1 because of the space
    nparsed += space_index + 1
    if nparsed > constants.MAX_REQ_METHOD_LEN:
        raise errors.InvalidToken(
            'Exceeded max request method length of {}'.format(
                constants.MAX_REQ_METHOD_LEN
            ))

    # +1 to include the space, and then .strip to ignore it.
    buf.advance(space_index + 1)
    raw_method = bytes(buf.slice()).strip()

    if not _is_token(raw_method):
        raise errors.InvalidToken('Expected token in HTTP method')

    method = raw_method.decode('utf-8')
    return (method, nparsed)


def _recv_code(buf: bytedata.Bytes) -> Optional[int]:
    """Receive the HTTP status code in ``buf``."""
    if len(buf) < 3:
        # Not enough bytes.
        return None

    buf.advance(3)
    raw_code = bytes(buf.slice())
    if not _are_digits(raw_code):
        raise errors.InvalidStatus('Expected only digits in status code!')

    return int(raw_code)


def _recv_reason(buf: bytedata.Bytes, allow_lf: bool) -> Optional[Tuple[str, int]]:
    """Receive the HTTP reason phrase.

    This function assumes that the reason phrase exists, so if you wish
    to make the reason phrase optional, you must check for its existence
    yourself.

    Returns the reason phrase and an integer representing the number of
    bytes parsed.
    """
    nparsed = 0
    crlf_index = find_newline(buf, b'\r\n')
    has_crlf = bool(~crlf_index)

    if not has_crlf:
        # Try getting an LF.
        lf_index = find_newline(buf, b'\n')
        has_lf = bool(~lf_index)
        if not has_lf:
            # Hmmm...
            if len(buf) > constants.MAX_HEADER_VAL_SIZE:
                # There should be a newline, since there are many more
                # characters than the maximum allowed in a header value.
                raise errors.InvalidStatus('Reason phrase too large!')
            # Otherwise, it's incomplete.
            return None

        # Wild LF on the scene.
        if not allow_lf:
            raise errors.NewlineError('CRLF is required!')

        # We have an LF!
        nparsed += lf_index + 1
        if (nparsed - 1) > constants.MAX_HEADER_VAL_SIZE:
            raise errors.InvalidStatus('Reason phrase too large!')
        buf.advance(lf_index + 1)
        raw_reason = bytes(buf.slice()).strip()
    else:
        # We have a CRLF.
        nparsed += crlf_index + 2
        if (nparsed - 2) > constants.MAX_HEADER_VAL_SIZE:
            raise errors.InvalidStatus('Reason phrase too large!')
        buf.advance(crlf_index + 2)
        raw_reason = bytes(buf.slice()).strip()

    if not _is_vchar_or_whsp(raw_reason):
        # Check for obsolete text.
        if not _is_obs_text(
                raw_reason.translate(None, constants.VCHAR_OR_WSP)):
            raise errors.InvalidStatus(
                'Invalid characters in response reason phrase!')
        # We has obsolete text.
        return ('', nparsed)
    return (raw_reason.decode('utf-8'), nparsed)


def _recv_header_name(buf: bytedata.Bytes) -> Optional[Tuple[str, int]]:
    """Receive a HTTP header field name from ``buf``.

    This method does NOT treat newlines (``\\n`` or ``\\r\\n``) as the end
    of HTTP headers. That means, any newlines will be handled as if they were
    invalid header characters. You must check for newlines yourself.

    Returns a tuple containing the header field name and the number of bytes parsed.
    """
    nparsed = 0
    colon_index = buf.find(_COLON)
    has_colon = bool(~colon_index)

    if not has_colon:
        # If there are more characters in the data than the maximum allowed
        # characters in a header name, then something's invalid.
        if len(buf) > constants.MAX_HEADER_NAME_LEN:
            raise errors.InvalidToken('Header name too long!')
        # Otherwise, it's incomplete.
        return None

    if colon_index < 1:
        # Tokens must be at least 1 char long. Header names are tokens.
        raise errors.InvalidToken(
            'Tokens must be at least one char long.')
    # +1 because of the colon.
    nparsed += colon_index + 1
    if nparsed - 1 > constants.MAX_HEADER_NAME_LEN:
        raise errors.InvalidToken('Header name too long!')

    # Get header name and colon.
    buf.advance(colon_index + 1)
    # Slice the buffer and remove the colon.
    raw_header_name = bytes(buf.slice()[:-1])
    if not _is_token(raw_header_name):
        raise errors.InvalidToken(
            'Invalid characters in header name!')

    return (raw_header_name.decode('utf-8'), nparsed)


def _recv_header_value(buf: bytedata.Bytes, allow_lf: bool) -> Optional[Tuple[str, int]]:
    """Receive a HTTP header field value from ``buf``.

    This function will "eat" (i.e. ignore and drop) any whitespace that appears
    before any other characters in the field value.
    """
    nparsed = 0
    # Now, get the header value.
    # We only look for CRLF first, since it's the preferred newline type
    # and so we spend less time looking for something we won't need.
    crlf_index = find_newline(buf, b'\r\n')
    has_crlf = bool(~crlf_index)

    if not has_crlf:
        # Try getting an LF.
        lf_index = find_newline(buf, b'\n')
        has_lf = bool(~lf_index)
        if not has_lf:
            # Hmmm...
            if len(buf) > constants.MAX_HEADER_VAL_SIZE:
                # There should be a newline, since there are many more
                # characters than the maximum allowed in a header value.
                raise errors.InvalidHeaderVal('Header field value too large!')
            # Otherwise, it's incomplete.
            return None

        # Wild LF on the scene.
        if not allow_lf:
            raise errors.NewlineError('CRLF is required!')

        # We have an LF!
        nparsed += lf_index + 1
        if (nparsed - 1) > constants.MAX_HEADER_VAL_SIZE:
            raise errors.InvalidHeaderVal('Header field value too large!')
        buf.advance(lf_index + 1)
        raw_header_val = bytes(buf.slice()).strip()
    else:
        # We have a CRLF.
        nparsed += crlf_index + 2
        if (nparsed - 2) > constants.MAX_HEADER_VAL_SIZE:
            raise errors.InvalidHeaderVal('Header field value too large!')
        buf.advance(crlf_index + 2)
        raw_header_val = bytes(buf.slice()).strip()

    # Delete all valid characters. Any characters left are possibly invalid.
    if not _is_vchar_or_whsp(raw_header_val):
        # Check for obsolete text.
        if not _is_obs_text(
                raw_header_val.translate(None, constants.VCHAR_OR_WSP)):
            raise errors.InvalidHeaderVal(
                'Invalid characters in header value!')

        # We has obsolete text.
        return ('', nparsed)

    return (raw_header_val.decode('utf-8'), nparsed)


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
