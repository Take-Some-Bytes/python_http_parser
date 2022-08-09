"""
``python_http_parser.body`` module.

This module provides classes to process HTTP bodies, and an abstract base
class called ``BodyProcessor`` to represent a generic class that processes
HTTP bodies.
"""

__all__ = [
    'BodyProcessor',
    'FixedLenProcessor',
    'ChunkedProcessor',
]

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple
# Compatibility requires us to use typing_extensions.
from typing_extensions import TypedDict

from . import constants, errors
from .helpers.newline import NewlineType, find_newline, startswith_newline


class BodyProcessorCallbacks(TypedDict):
    """
    Typed dictionary of all the callbacks that could be registered in a BodyProcessor.
    """
    error: Callable[[Exception], None]
    data: Callable[[bytes], None]
    finished: Callable[[], None]


_SEMI = 0x3b


class BodyProcessor(ABC):
    """A BodyProcessor is able to process a HTTP body."""

    def __init__(self) -> None:
        """Create a new BodyProcessor.

        A BodyProcessor is able to process a HTTP body.
        """
        self.callbacks: BodyProcessorCallbacks = {
            'error': lambda _: None,
            'data': lambda _: None,
            'finished': lambda: None
        }

    def on_error(self, callback: Callable[[Exception], None]) -> None:
        """Register the specified function to be called on an error."""
        self.callbacks['error'] = callback

    def on_data(self, callback: Callable[[bytes], None]) -> None:
        """Register the specified function to be called when data is available."""
        self.callbacks['data'] = callback

    def on_finished(self, callback: Callable[[], None]) -> None:
        """Register the specified function to be called when the body has finished."""
        self.callbacks['finished'] = callback

    @abstractmethod
    def process(self, chunk: bytes, allow_lf: bool) -> int:
        """Process the next few bytes as part of the HTTP body.

        Returns the number of bytes processed. If an error occurred
        during processing of the chunk, -1 is returned.
        """
        raise NotImplementedError()


class FixedLenProcessor(BodyProcessor):
    """A FixedLenProcessor processes HTTP bodies with a fixed length."""

    def __init__(self, body_len: int) -> None:
        """Create a new FixedLenProcessor.

        A FixedLenProcessor processes HTTP bodies with a fixed length. This
        is usually used when a HTTP message has a ``Content-Length`` header,
        denoting a body with a known length.

        All this processor does is keep track of how much bytes have currently
        been processed, and how much more still needs to be received.
        """
        super().__init__()

        self.expected_len = body_len
        self.received_len = 0
        self.finished = False

    def process(self, chunk: bytes, _: bool = True) -> int:
        """Process the next few bytes as part of the HTTP body.

        Returns the number of bytes processed. If an error occurred
        during processing of the chunk, -1 is returned.
        """
        nprocessed = 0
        chunk_len = len(chunk)
        data_cb, error_cb, finished_cb = (
            self.callbacks['data'],
            self.callbacks['error'],
            self.callbacks['finished']
        )

        if self.finished:
            # Uh oh--processing already finished.
            error_cb(errors.DoneError())
            return -1

        if chunk_len + self.received_len <= self.expected_len:
            # Still within the body length limit.
            self.received_len += chunk_len
            nprocessed += chunk_len
            data_cb(chunk)
        else:
            # Whoa! We got extra bytes.
            expected_size = self.expected_len - self.received_len
            if expected_size < 0:
                # Huh?
                error_cb(ValueError('Body length is negative!'))
                return -1

            expected_chunk = chunk[:expected_size]
            self.received_len += expected_size
            nprocessed += expected_size
            data_cb(expected_chunk)

        if self.received_len == self.expected_len:
            # We are finished!
            self.finished = True
            finished_cb()

        return nprocessed


class ChunkedProcessor(BodyProcessor):
    """A ChunkedProcessor processes chunked HTTP bodies."""

    def __init__(self) -> None:
        """Create a new ChunkedProcessor.

        A ChunkedProcessor processes chunked HTTP bodies which do not have a
        known size. This class imposes no limits on the maximum amount of
        chunks; that is a job for the user of this class. BUT, this class DOES
        impose a maximum size for EACH CHUNK: 16777216 bytes, or 16MiB. Any chunk
        that is encountered which is larger than that will cause this processor
        to immediately stop and error out.

        Chunk extensions are not parsed, and are limited to 4KiB per chunk.
        """
        super().__init__()

        self.finished = False
        self.had_error = False
        # None means no chunk is expected.
        self.next_chunk_size: Optional[int] = None
        self.expecting_extensions = False
        self.extensions: List[str] = []

    def _parse_chunk_size(self, buf: bytes, allow_lf: bool) -> Tuple[int, bytes]:
        """
        Parse a chunk's size.

        Return the number of bytes parsed and the remaining bytes.
        """
        nprocessed = 0
        result = _parse_chunk_size(buf, allow_lf)
        if result is None:
            # Incomplete.
            return (nprocessed, buf)

        chunk_size, parsed, expecting_extensions = result

        self.next_chunk_size = chunk_size
        self.expecting_extensions = expecting_extensions
        nprocessed += parsed

        return (nprocessed, buf[nprocessed:])

    def _parse_chunk_extensions(self, buf: bytes, allow_lf: bool) -> Tuple[int, bytes]:
        """
        Parse a chunk's extensions, if any.

        Return the number of bytes parsed and the remaining bytes.
        """
        nprocessed = 0

        # Receive chunk extensions, but do not parse them.
        result = _recv_chunk_extensions(buf, allow_lf)
        if result is None:
            self.expecting_extensions = True
            return (nprocessed, buf)
        self.expecting_extensions = False

        extensions, parsed = result
        nprocessed += parsed
        if len(extensions) > 0:
            # We have extensions!
            self.extensions.append(extensions)

        return (nprocessed, buf[parsed:])

    def _process_chunk(self, buf: bytes, allow_lf: bool) -> Optional[Tuple[int, bytes]]:
        """
        Process a chunk which has size ``self.next_chunk_size``.

        None is returned if there is not enough data. Returns the number of
        bytes processed and the remaining bytes.
        """
        nprocessed = 0
        if self.next_chunk_size is None:
            # What.
            raise TypeError('Trying to parse chunk when size is None')

        if len(buf) < self.next_chunk_size:
            # Not enough data.
            return None
        # buf.advance(self.next_chunk_size)
        nprocessed += self.next_chunk_size

        # Get the chunk's contents and drop them
        chunk_contents = buf[:self.next_chunk_size]
        buf = buf[self.next_chunk_size:]

        # There should be a newline after the chunk contents
        n_result = startswith_newline(buf, allow_lf)
        if n_result is None:
            # Incomplete.
            return None

        is_newline, newline_type = n_result
        if not is_newline:
            # There MUST be a newline after a chunk
            raise errors.InvalidChunk(
                'Expected newline to signify end-of-chunk!')

        # Process the newline
        newline_len = 2 if newline_type is NewlineType.CRLF else 1
        nprocessed += newline_len
        buf = buf[newline_len:]

        if self.next_chunk_size == 0:
            # That was the last chunk.
            self.finished = True
            self.next_chunk_size = None
            self.callbacks['finished']()
            return (nprocessed, buf)

        self.callbacks['data'](chunk_contents)
        self.next_chunk_size = None
        return (nprocessed, buf)

    def _process(self, buf: bytes, allow_lf: bool) -> int:
        """Internal ``._process()`` method.

        Contains the processor directing logic. All errors will be propagated
        back to the caller.
        """
        nprocessed = 0

        while not self.finished:
            if self.next_chunk_size is None:
                # Parse chunk size.
                parsed, rest = self._parse_chunk_size(buf, allow_lf)

                nprocessed += parsed
                buf = rest
            if self.next_chunk_size is None:
                # If there was not enough data to parse a full chunk size, don't go on.
                break
            if self.expecting_extensions:
                # We are expecting chunk extensions.
                parsed, rest = self._parse_chunk_extensions(buf, allow_lf)

                nprocessed += parsed
                buf = rest
            if self.expecting_extensions:
                # There wasn't enough data.
                break

            ret = self._process_chunk(buf, allow_lf)
            if ret is None:
                # Not enough data.
                break

            parsed, rest = ret

            nprocessed += parsed
            buf = rest

        return nprocessed

    def process(self, chunk: bytes, allow_lf: bool) -> int:
        """Process ``chunk`` as a part of the HTTP body."""
        if self.finished:
            self.callbacks['error'](errors.DoneError(
                'BodyProcessor is finished.'))
            self.had_error = True

        if self.had_error:
            # Don't even try.
            return -1

        try:
            return self._process(chunk, allow_lf)
        except (errors.NewlineError, errors.InvalidChunkSize,
                errors.InvalidChunk, errors.InvalidChunkExtensions,
                UnicodeDecodeError) as ex:
            self.callbacks['error'](ex)
            self.had_error = True
            return -1


def _parse_chunk_size(buf: bytes, allow_lf: bool) -> Optional[Tuple[int, int, bool]]:
    """Parse and return the chunk size contained in ``buf``.

    Return a tuple containing the parsed chunk size, the number of bytes parsed,
    and if chunk extensions are expected.
    None is returned if there weren't enough bytes.
    """
    nparsed = 0

    semi_index = buf.find(_SEMI)
    newline_idx, newline_type = find_newline(buf, allow_lf)

    has_newline = bool(~newline_idx)
    has_semi = bool(~semi_index)

    if not has_semi and not has_newline:
        if len(buf) > constants.MAX_CHUNK_SIZE_DIGITS:
            # There should be enough bytes for a valid chunk size.
            raise errors.InvalidChunkSize('Chunk size too large!')
        # Incomplete.
        return None

    # Only assume there are chunk extensions if the semicolon appears
    # in front of the LF and CRLF (if any).
    if has_semi and ((semi_index < newline_idx) or not has_newline):
        # There are chunk extensions.
        nparsed += semi_index
        raw_chunk_size = buf[:semi_index]
        has_chunk_extensions = True

        # Process the semicolon
        nparsed += 1
    else:
        # No chunk extensions
        nparsed += newline_idx
        raw_chunk_size = buf[:newline_idx]
        has_chunk_extensions = False

        # Process the newline
        nparsed += 2 if newline_type is NewlineType.CRLF else 1

    if not _are_hex_digits(raw_chunk_size):
        # Chunk size must only contain hexadecimal digits.
        raise errors.InvalidChunkSize(
            'Chunk size must only contain hexadecimal digits!')

    chunk_size = int(raw_chunk_size, 16)
    if chunk_size > constants.MAX_CHUNK_SIZE:
        raise errors.InvalidChunkSize('Chunk size too large!')
    return (chunk_size, nparsed, has_chunk_extensions)


def _recv_chunk_extensions(buf: bytes, allow_lf: bool) -> Optional[Tuple[str, int]]:
    """Receive all chunk extensions up to a newline. Return the extensions
    and number of bytes parsed.

    This method does not validate or parse chunk extensions. The size of
    chunk extensions is limited to 4KiB.
    """
    nrecved = 0

    newline_idx, newline_type = find_newline(buf, allow_lf)
    has_newline = bool(~newline_idx)
    if not has_newline:
        if len(buf) > constants.MAX_CHUNK_EXTENSION_SIZE:
            # Chunk extensions are too large.
            raise errors.InvalidChunkExtensions(
                'Chunk extensions too large! Max 4KiB per chunk.')

        # Otherwise, incomplete.
        return None

    nrecved += newline_idx

    # Receive extensions
    raw_extensions = buf[nrecved:]

    # Account for the newline
    nrecved += 2 if newline_type is NewlineType.CRLF else 1

    return (raw_extensions.decode('utf-8'), nrecved)


def _are_hex_digits(_bytes: bytes) -> bool:
    """Are the bytes in ``_bytes`` all valid hex digits?"""
    return len(_bytes.translate(None, constants.HEX_DIGITS)) == 0
