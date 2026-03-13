"""PuDB integration (curses TUI debugger)."""

from devliverepl.capture import get_current_context
import sys


def attach(frame=None):
    """Attach PuDB debugger with captured context.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.

    Raises:
        ImportError: If PuDB is not installed.

    Example:
        >>> from devliverepl.integrations.pudb import attach
        >>> attach()  # Drops into PuDB with captured context
    """
    try:
        import pudb
    except ImportError:
        print("PuDB is not installed.")
        print("Install with: pip install pudb")
        print("Or with uv: uv add pudb")
        return

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        frame = sys._getframe(1)

    pudb.set_trace(frame=frame)


# Check availability
try:
    import pudb
    available = True
except ImportError:
    available = False

__all__ = ["attach", "available"]
