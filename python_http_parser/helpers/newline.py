"""Newline-related helper functions."""
from enum import Enum

from typing import Optional, Tuple, Union

from .. import errors

_LF = 0x0a
_CR = 0x0d


class NewlineType(Enum):
    """
    The type of the newline.

    CR is not considered a valid newline type.
    """
    LF = 0
    CRLF = 1
    NONE = 2


def startswith_newline(buf: Union[bytes, bytearray], allow_lf: bool) -> Optional[Tuple[bool, NewlineType]]:
    """Does the buffer start with a newline?"""
    buf_len = len(buf)

    is_cr = buf.startswith(b'\r')
    if is_cr:
        if buf_len < 2:
            # Incomplete.
            return None
        if not buf.startswith(b'\r\n'):
            # Bare CR.
            raise errors.NewlineError(
                'Expected CRLF, received bare CR.')

        # It's a CRLF.
        return (True, NewlineType.CRLF)

    is_lf = buf.startswith(b'\n')
    if is_lf:
        if not allow_lf:
            raise errors.NewlineError('CRLF is required!')

        # It's LF.
        return (True, NewlineType.LF)

    if buf_len < 1:
        # Incomplete.
        return None

    # No newline :(
    return (False, NewlineType.NONE)


def find_newline(buf: Union[bytes, bytearray], allow_lf: bool) -> Tuple[int, NewlineType]:
    """
    Look for the a newline in ``buf``.

    Return the index and type of newline that is found, or -1 if a newline could
    not be found. Will throw an error if a bare CR is encountered.
    """
    buf_len = len(buf)

    lf_index = buf.find(_LF)
    cr_index = buf.find(_CR)
    has_lf = bool(~lf_index)
    has_cr = bool(~cr_index)

    if not has_cr and not has_lf:
        return (-1, NewlineType.NONE)

    if has_cr:
        if cr_index == buf_len - 1:
            # There could be an LF after the CR we found.
            return (-1, NewlineType.NONE)

        if buf[cr_index + 1] != _LF:
            raise errors.NewlineError('Expected CRLF, received bare CR!')

        # It's CRLF
        return (cr_index, NewlineType.CRLF)
    if has_lf:
        if not allow_lf:
            raise errors.NewlineError('CRLF is required.')

        # It's LF
        return (lf_index, NewlineType.LF)

    # Should be unreachable
    return (-1, NewlineType.NONE)
