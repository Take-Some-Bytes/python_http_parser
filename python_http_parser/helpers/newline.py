"""Newline-related helper functions."""
from typing import Optional, Union, Sized
# Use typing_extensions to maintain compatibility.
from typing_extensions import Literal, SupportsIndex, Protocol

from .. import bytedata, errors

_LF = 0x0a
_CR = 0x0d

class HasFind(Sized, Protocol):
    """A type that has a .find() method."""
    # pylint: disable=abstract-method,missing-function-docstring,too-few-public-methods

    def find(
        self, __sub: Union[bytes, int],
        __start: Optional[SupportsIndex] = ...,
        __end: Optional[SupportsIndex] = ...
    ) -> int: ...


def find_newline(_bytes: HasFind, newline_type: Literal[b'\n', b'\r\n']) -> int:
    """
    Look for the specified newline in ``_bytes``. Return the index where
    it is found, or -1 if the newline could not be found. Will throw an erro
    if a bare CR is encountered.
    """
    lf_index = _bytes.find(_LF)
    cr_index = _bytes.find(_CR)
    has_lf = bool(~lf_index)
    has_cr = bool(~cr_index)
    if not has_lf and has_cr:
        # Hold it...
        if cr_index == len(_bytes) - 1:
            # There could be an LF after the CR we found.
            return -1
        # It's a bare CR!
        raise errors.NewlineError('Expected CRLF, received bare CR!')
    if not has_lf:
        # All newlines we accept have LF in them.
        return -1

    if newline_type == b'\n':
        return lf_index

    # We are expecting a CRLF.
    if not has_cr:
        # No CR, no CRLF.
        return -1
    return cr_index

def is_newline(buf: bytedata.Bytes, newline_type: Literal[b'\n', b'\r\n']) -> Optional[bool]:
    """Is the next byte or two of ``buf`` a newline?

    Return None if there weren't enough bytes.
    """
    byte = buf.peek()
    if byte is None:
        return None
    if byte == _LF and newline_type[0] == _LF:
        buf.bump()
        return True

    if byte == _CR and newline_type[0] == _CR:
        buf.bump()
        next_byte = next(buf, None)
        if next_byte is None:
            return None
        if next_byte != _LF:
            raise errors.NewlineError(
                'Expected CRLF, received bare CR.')
        return True

    return False
