"""Frame capture and context extraction for devliverepl."""

from __future__ import annotations

import dataclasses
import inspect
import threading
from typing import Any, Optional


@dataclasses.dataclass
class CapturedContext:
    """Context captured from a call site.

    Attributes:
        locals: Local variables from the captured frame.
        globals: Global variables from the captured frame.
        filename: Source file path.
        lineno: Line number where capture occurred.
        function: Function name where capture occurred.
        frame: The captured frame object (or None if unavailable).
    """
    locals: dict[str, Any]
    globals: dict[str, Any]
    filename: str
    lineno: int
    function: str
    frame: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Merge locals and globals into a single dict for REPL namespace."""
        result = {}
        result.update(self.globals)
        result.update(self.locals)
        return result


def capture_call_site() -> CapturedContext:
    """Capture the calling frame's context.

    This function captures locals and globals from the frame that called
    the function which called capture_call_site() (i.e., the user's code).

    Returns:
        A CapturedContext containing the captured state.
    """
    # Get the current frame
    frame = inspect.currentframe()

    # Walk up the stack to find the user's call site
    # We need to skip past:
    # - Frame 0: capture_call_site
    # - Frame 1: direct caller (might be internal wrapper)
    # Look for a frame that's not in this module
    user_frame = None
    f = frame
    skip_count = 0

    while f is not None and skip_count < 10:  # Limit iterations
        skip_count += 1
        f = f.f_back
        if f is None:
            break

        # Skip frames from this module
        module_name = f.f_globals.get('__name__', '')
        if not module_name.startswith('devliverepl'):
            user_frame = f
            break

    if user_frame is None and frame is not None:
        # Fallback to caller's caller
        user_frame = frame.f_back.f_back if frame.f_back else None

    if user_frame is None:
        # No frame available, return empty context
        return CapturedContext(
            locals={},
            globals={},
            filename="<unknown>",
            lineno=0,
            function="<unknown>",
            frame=None,
        )

    # Capture locals and globals
    # Use copy() to avoid holding references that prevent GC
    locals_dict = dict(user_frame.f_locals)
    globals_dict = dict(user_frame.f_globals)

    # Get frame info
    filename = user_frame.f_code.co_filename
    lineno = user_frame.f_lineno
    function = user_frame.f_code.co_name

    return CapturedContext(
        locals=locals_dict,
        globals=globals_dict,
        filename=filename,
        lineno=lineno,
        function=function,
        frame=user_frame,
    )


class ContextRegistry:
    """Thread-safe registry for captured contexts."""

    def __init__(self) -> None:
        self._contexts: dict[str, CapturedContext] = {}
        self._lock = threading.RLock()
        self._order: list[str] = []  # Track insertion order

    def store(self, name: str, context: CapturedContext) -> None:
        """Store a context with the given name.

        Args:
            name: Identifier for this context.
            context: The captured context to store.
        """
        with self._lock:
            if name not in self._contexts:
                self._order.append(name)
            self._contexts[name] = context

    def get(self, name: str) -> Optional[CapturedContext]:
        """Retrieve a stored context by name.

        Args:
            name: Identifier of the context to retrieve.

        Returns:
            The CapturedContext, or None if not found.
        """
        with self._lock:
            return self._contexts.get(name)

    def get_latest(self) -> Optional[CapturedContext]:
        """Get the most recently stored context.

        Returns:
            The most recent CapturedContext, or None if empty.
        """
        with self._lock:
            if not self._order:
                return None
            return self._contexts.get(self._order[-1])

    def list_names(self) -> list[str]:
        """List all stored context names.

        Returns:
            List of context names in insertion order.
        """
        with self._lock:
            return list(self._order)

    def clear(self) -> None:
        """Remove all stored contexts."""
        with self._lock:
            self._contexts.clear()
            self._order.clear()


# Global context registry
_context_registry = ContextRegistry()


def get_current_context() -> Optional[CapturedContext]:
    """Get the most recently captured context.

    Returns:
        The latest CapturedContext, or None if no context exists.
    """
    return _context_registry.get_latest()


def get_context_registry() -> ContextRegistry:
    """Get the global context registry.

    Returns:
        The global ContextRegistry instance.
    """
    return _context_registry
