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

try:
    from typing import TypedDict

    class BodyProcessorCallbacks(TypedDict):
        """
        Typed dictionary of all the callbacks that could be registered in a BodyProcessor.
        """
        error: Callable[[Exception], None]
        data: Callable[[bytes], None]
        finished: Callable[[], None]
except ImportError:
    from typing import Mapping
    # TypedDict is not available below Python 3.8
    BodyProcessorCallbacks = Mapping[str, Callable]

from . import bytedata, constants, errors
from .helpers.newline import find_newline, is_newline

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
        self.next_chunk_size = None
        self.expecting_extensions = False
        self.extensions: List[str] = []

    def _parse_chunk_size(self, buf: bytedata.Bytes, allow_lf: bool) -> int:
        """Parse a chunk's size. Return the number of bytes parsed."""
        nprocessed = 0
        result = _parse_chunk_size(buf, allow_lf)
        if result is None:
            # Incomplete.
            return nprocessed

        chunk_size, parsed, expecting_extensions = result
        self.next_chunk_size = chunk_size
        self.expecting_extensions = expecting_extensions
        nprocessed += parsed

        return nprocessed

    def _parse_chunk_extensions(self, buf: bytedata.Bytes, allow_lf: bool) -> int:
        """Parse a chunk's extensions, if any. Return the number of bytes parsed."""
        nprocessed = 0

        # Receive chunk extensions, but do not parse them.
        result = _recv_chunk_extensions(buf, allow_lf)
        if result is None:
            self.expecting_extensions = True
            return nprocessed
        self.expecting_extensions = False
        extensions, parsed = result
        nprocessed += parsed
        if len(extensions) > 0:
            # We have extensions!
            self.extensions.append(extensions)

        return nprocessed

    def _process_chunk(self, buf: bytedata.Bytes, allow_lf: bool) -> Optional[int]:
        """Process a chunk which has size ``self.next_chunk_size``.

        None is returned if there is not enough data.
        """
        nprocessed = 0
        if len(buf) < self.next_chunk_size:
            # Not enough data.
            return None
        buf.advance(self.next_chunk_size)
        nprocessed += self.next_chunk_size

        is_lf = is_newline(buf, b'\n')
        is_crlf = is_newline(buf, b'\r\n')
        if is_lf is None and is_crlf is None:
            # Incomplete.
            return None
        if not is_lf and not is_crlf:
            # Hmm... let's see.
            if len(buf) > self.next_chunk_size:
                # There SHOULD be a newline.
                raise errors.InvalidChunk(
                    'Expected newline to signify end-of-chunk!')
            # Otherwise, it's incomplete.
            return None
        if is_lf:
            # Wild LF on the scene. Proceed with caution.
            if not allow_lf:
                raise errors.NewlineError(
                    'CRLF is required.')
            # All good.
            nprocessed += 1
            # Skip the last byte, which is a LF.
            chunk = bytes(buf.slice()[:-1])
        else:
            # It's CRLF. No caution needed.
            nprocessed += 2
            # Ignore the last 2 bytes, which is CRLF.
            chunk = bytes(buf.slice()[:-2])

        if self.next_chunk_size == 0:
            # That was the last chunk.
            self.finished = True
            self.next_chunk_size = None
            self.callbacks['finished']()
            return nprocessed

        self.callbacks['data'](chunk)
        self.next_chunk_size = None
        return nprocessed

    def _process(self, buf: bytedata.Bytes, allow_lf: bool) -> int:
        """Internal ``._process()`` method.

        Contains the processor directing logic. All errors will be propagated
        back to the caller.
        """
        nprocessed = 0

        while not self.finished:
            if self.next_chunk_size is None:
                # Parse chunk size.
                nprocessed += self._parse_chunk_size(buf, allow_lf)
            if self.next_chunk_size is None:
                # If there was not enough data to parse a full chunk size, don't go on.
                break
            if self.expecting_extensions:
                # We are expecting chunk extensions.
                nprocessed += self._parse_chunk_extensions(buf, allow_lf)
            if self.expecting_extensions:
                # There wasn't enough data.
                break

            ret = self._process_chunk(buf, allow_lf)
            if ret is None:
                # Not enough data.
                break

            nprocessed += ret

        return nprocessed

    def process(self, chunk: bytes, allow_lf: bool) -> int:
        """Process ``chunk`` as a part of the HTTP body."""
        buf = bytedata.Bytes(chunk)
        if self.finished:
            self.callbacks['error'](errors.DoneError(
                'BodyProcessor is finished.'))
            self.had_error = True

        if self.had_error:
            # Don't even try.
            return -1

        try:
            return self._process(buf, allow_lf)
        except (errors.NewlineError, errors.InvalidChunkSize,
                errors.InvalidChunk, errors.InvalidChunkExtensions,
                UnicodeDecodeError) as ex:
            self.callbacks['error'](ex)
            self.had_error = True
            return -1


def _parse_chunk_size(buf: bytedata.Bytes, allow_lf: bool) -> Optional[Tuple[int, int, bool]]:
    """Parse and return the chunk size contained in ``buf``.

    Return a tuple containing the parsed chunk size, the number of bytes parsed,
    and if chunk extensions are expected.
    None is returned if there weren't enough bytes.
    """
    nparsed = 0
    lf_index = find_newline(buf, b'\n')
    crlf_index = find_newline(buf, b'\r\n')
    semi_index = buf.find(_SEMI)
    has_lf = bool(~lf_index)
    has_crlf = bool(~crlf_index)
    has_semi = bool(~semi_index)
    if not has_semi and not has_lf and not has_crlf:
        # Hmmm...
        if len(buf) > constants.MAX_CHUNK_SIZE_DIGITS:
            # There should be enough bytes for a valid chunk size.
            raise errors.InvalidChunkSize('Chunk size too large!')
        # Incomplete.
        return None

    # Only assume there are chunk extensions if the semicolon appears
    # in front of the LF and CRLF (if any).
    if (has_semi
        and (semi_index < lf_index if has_lf else True)
            and (semi_index < crlf_index if has_crlf else True)):
        # There are chunk extensions.
        nparsed += semi_index
        buf.advance(semi_index)
        raw_chunk_size = bytes(buf.slice())
        has_chunk_extensions = True
    elif has_lf and not has_crlf:
        # It's a wild LF on the scene.
        if not allow_lf:
            # LF is not allowed. CRLF forever!
            raise errors.NewlineError('CRLF is required.')
        # Chunk size is everything up to lf_index.
        # Like always, +1 to include the LF, then [:-1] to ignore it.
        nparsed += lf_index + 1
        buf.advance(lf_index + 1)
        raw_chunk_size = bytes(buf.slice()[:-1])
        has_chunk_extensions = False
    else:
        # It's a CRLF. No caution needed.
        # +2 to include the CRLF, then [:-2] to ignore it.
        nparsed += crlf_index + 2
        buf.advance(crlf_index + 2)
        raw_chunk_size = bytes(buf.slice()[:-2])
        has_chunk_extensions = False

    if not _are_hex_digits(raw_chunk_size):
        # Chunk size must only contain hexadecimal digits.
        raise errors.InvalidChunkSize(
            'Chunk size must only contain hexadecimal digits!')

    chunk_size = int(raw_chunk_size, 16)
    if chunk_size > constants.MAX_CHUNK_SIZE:
        raise errors.InvalidChunkSize('Chunk size too large!')
    return (chunk_size, nparsed, has_chunk_extensions)


def _recv_chunk_extensions(buf: bytedata.Bytes, allow_lf: bool) -> Optional[Tuple[str, int]]:
    """Receive all chunk extensions up to a newline. Return the extensions
    and number of bytes parsed.

    This method does not validate or parse chunk extensions. The size of
    chunk extensions is limited to 4KiB.
    """
    nrecved = 0
    lf_index = find_newline(buf, b'\n')
    crlf_index = find_newline(buf, b'\r\n')
    has_lf = bool(~lf_index)
    has_crlf = bool(~crlf_index)
    if not has_lf and not has_crlf:
        # Hmm....
        if len(buf) > constants.MAX_CHUNK_EXTENSION_SIZE:
            # Chunk extensions are too large.
            raise errors.InvalidChunkExtensions(
                'Chunk extensions too large! Max 4KiB per chunk.')

        # Otherwise, incomplete.
        return None
    if has_lf and not has_crlf:
        # Wild LF on the scene. Proceed with caution.
        if not allow_lf:
            raise errors.NewlineError('CRLF is required.')
        if lf_index == 0:
            # There are zero chunk extensions.
            nrecved += 1
            buf.bump().slice()
            return ('', nrecved)

        # Everything up to lf_index are chunk extensions.
        nrecved += lf_index + 1
        buf.advance(lf_index + 1)
        # Ignore the LF.
        raw_extensions = bytes(buf.slice()[:-1])
    else:
        # It's a CRLF.
        if crlf_index == 0:
            # No chunk extensions.
            nrecved += 2
            buf.advance(2).slice()
            return ('', nrecved)

        # +2 to include the CRLF, and [:-2] to ignore it.
        nrecved += crlf_index + 2
        buf.advance(crlf_index + 2)
        raw_extensions = bytes(buf.slice()[:-2])

    return (raw_extensions.decode('utf-8'), nrecved)


def _are_hex_digits(_bytes: bytes) -> bool:
    """Are the bytes in ``_bytes`` all valid hex digits?"""
    return len(_bytes.translate(None, constants.HEX_DIGITS)) == 0
