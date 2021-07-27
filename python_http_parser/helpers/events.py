"""Custom EventEmitter class."""
__all__ = [
    'EventEmitter'
]

from typing import Any, Callable, Dict, List


class Listener:
    """A Listener object represents a listening that listens on a event."""

    __slots__ = ['callback', 'once']

    def __init__(self, callback: Callable, is_once: bool) -> None:
        super().__init__()

        self.callback = callback
        self.once = is_once

    def __hash__(self) -> int:
        return hash(self.callback) + hash(self.once)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.callback(*args, **kwargs)


class EventEmitter:
    """Simple, custom EventEmitter class."""

    def __init__(self) -> None:
        """Create a new EventEmitter."""
        self._listeners: Dict[str, List[Listener]] = {}

    def on(self, event: str, callback: Callable) -> None:  # pylint: disable=invalid-name
        """Register a new listener for ``event``."""
        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(Listener(callback, False))

    def once(self, event: str, callback: Callable) -> None:
        """Register a new listener for ``event`` that will only be called once."""
        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(Listener(callback, True))

    def off(self, event: str, callback: Callable) -> None:
        """Remove a listener from ``event``."""
        if event not in self._listeners:
            return

        listener_hashes = (hash(Listener(callback, True)), hash(Listener(callback, False)))
        def filter_func(listener: Listener):
            if hash(listener) in listener_hashes:
                return False
            return True

        self._listeners[event] = list(filter(filter_func, self._listeners[event]))

    def emit(self, event: str, *args, **kwargs) -> None:
        """Call any listeners listening for ``event`` with the specified arguments."""
        if event not in self._listeners:
            return

        stack = self._listeners[event].copy()
        for listener in stack:
            is_once = listener.once
            listener(*args, **kwargs)
            # Remove listener if it was a ``once`` listener.
            if is_once:
                self.off(event, listener.callback)

    def listeners(self, event: str) -> List[Callable]:
        """Return all listeners registered with ``event``."""
        if event not in self._listeners:
            return []

        return list(map(lambda listener: listener.callback, self._listeners[event]))
