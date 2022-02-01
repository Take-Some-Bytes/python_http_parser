"""
The ``python_http_parser.bytedata`` module is an internal module that provides
utilities for working with binary data (i.e. bytes).
"""

__all__ = [
    'Bytes',
]

from collections.abc import Iterator, Sized
from typing import Optional, Tuple, Union, Iterator as TypingIterator
# For compatibility with Python<3.8
from typing_extensions import SupportsIndex


class Bytes(Iterator, Sized):
    """An object wrapping a plain bytes object."""

    def __init__(self, data: bytes) -> None:
        """Create a new Bytes object that wraps the specified bytes object.

        This class is distinct from the ``bytes`` object from the Python
        standard library.

        A Bytes object is an immutable and unresizable sequence of bytes. It has
        a cursor that could be advanced, but not retracted. This makes it useful
        to consume data without actually modifying it.
        """
        self.view = memoryview(data)
        self.data = data
        self.data_len = len(data)
        self.pos = 0
        self.start = 0

    def __getitem__(self, index: int) -> int:
        return self.view[index]

    def __len__(self) -> int:
        return self.data_len - self.start

    def __iter__(self) -> TypingIterator[int]:
        return self

    def __next__(self) -> int:
        view = self.view[self.pos:]
        try:
            byte = view[0]
            self.bump()
            return byte
        except IndexError:
            # We don't care about preserving the stack trace here.
            # pylint: disable=raise-missing-from
            raise StopIteration

    def as_bytes(self) -> bytes:
        """Return this Bytes object's data as the built-in ``bytes`` object.

        This only returns data starting from ``self.pos``.
        """
        return bytes(self.view[self.pos:])

    def peek(self) -> Optional[int]:
        """Peek at the next byte without bumping the position of this Bytes object."""
        try:
            return self.view[self.pos]
        except IndexError:
            return None

    def bump(self) -> 'Bytes':
        """Bump the position of this Bytes object by 1.

        Does not perform bounds-checking. Returns this Bytes object
        for method chaining.
        """
        self.pos += 1
        self.start += 1
        return self

    def advance(self, amount: int) -> 'Bytes':
        """Advance the position of this Bytes object by ``amount``.

        Does not perform bounds-checking. Returns this Bytes object
        for method chaining.
        """
        self.pos += amount
        self.start += amount
        return self

    def slice(self) -> memoryview:
        """Remove all stored bytes until ``self.pos``.

        Returns the removed bytes.
        """
        return self.slice_skip(0)

    def slice_skip(self, skip: int) -> memoryview:
        """Remove all stored bytes until ``self.pos``, minus ``skip``."""
        head_pos = self.pos - skip
        self.start = self.start - skip
        head = self.view[:head_pos]
        tail = self.view[head_pos:]
        self.view = tail
        self.pos = 0

        return head

    # This function is only like this to satisfy the ``HasFind`` Protocol.
    def find(
        self, sub: Union[bytes, int],
        _s: Optional[SupportsIndex] = None,
        _e: Optional[SupportsIndex] = None
    ):
        """Return the lowest index where ``sub`` is found.

        ``start`` represents the offset which to start searching.
        """
        index = self.data.find(sub, self.start)
        if index < 0:
            return -1
        return index - self.start

    def next_8(self) -> Optional[bytes]:
        """Return the next 8 bytes, if they exist.

        Will advance the position of this Bytes object.
        """
        if len(self) >= 8:
            self.advance(8)
            return bytes(self.slice())
        return None


class Buffer(Iterator, Sized):
    """
    A Buffer class for quick reading of immutable byte objects.
    """

    def __init__(self, data: memoryview) -> None:
        """
        Create a new Buffer object.

        This class will *copy* the data within the memoryview. The starting copy
        is the only copy this class will make.
        """
        self.data = bytes(data)
        self.view = memoryview(self.data)
        self.data_len = len(self.data)

        self.cursor_pos = 0
        self.actual_data_start = 0

    def __len__(self) -> int:
        return self.data_len - self.actual_data_start

    def __iter__(self) -> TypingIterator[int]:
        return self

    def __next__(self) -> int:
        try:
            byte = self.view[self.cursor_pos]

            self.cursor_pos += 1
            self.actual_data_start += 1

            return byte
        except IndexError:
            # We don't care about preserving the stack trace here.
            # pylint: disable=raise-missing-from
            raise StopIteration

    def __getitem__(self, index: int) -> int:
        return self.view[self.cursor_pos + index]

    def to_bytes(self) -> bytes:
        """Convert this Buffer object's data to the builtin ``byte`` data structure.

        This only returns data starting from ``self.cursor_pos``.
        """
        return bytes(self.view[self.cursor_pos:])

    def bump(self):
        """Move this Buffer's cursor by 1."""
        self.cursor_pos += 1
        self.actual_data_start += 1

    def advance(self, amt: int):
        """Move this Buffer's cursor by amt."""
        self.cursor_pos += amt
        self.actual_data_start += amt

    def startswith(self, prefix: Union[bytes, Tuple[bytes]]) -> bool:
        """Return True if this Buffer object starts with the specified prefix, False otherwise."""
        return self.data.startswith(prefix, self.actual_data_start)

    def find(self, sub: Union[bytes, SupportsIndex]) -> int:
        """Return the lowest index in this Buffer object where subsection sub is found"""
        index = self.data.find(sub, self.actual_data_start)

        return -1 if index < 0 else (index - self.actual_data_start)

    def slice(self) -> memoryview:
        """Remove all stored bytes until ``self.pos``.

        Returns the removed bytes.
        """
        head = self.view[:self.cursor_pos]
        tail = self.view[self.cursor_pos:]
        self.view = tail
        self.cursor_pos = 0

        return head
