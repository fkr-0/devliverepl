"""IPython debugger (ipdb) integration."""

from devliverepl.capture import get_current_context
import sys


def attach(frame=None):
    """Attach ipdb debugger with captured context.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.

    Raises:
        ImportError: If ipdb is not installed.

    Example:
        >>> from devliverepl.integrations.ipdb import attach
        >>> attach()
    """
    try:
        import ipdb
    except ImportError:
        print("ipdb is not installed.")
        print("Install with: pip install ipdb")
        print("Or with uv: uv add ipdb")
        return

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        frame = sys._getframe(1)

    ipdb.set_trace(frame=frame)


# Check availability
try:
    import ipdb
    available = True
except ImportError:
    available = False

__all__ = ["attach", "available"]
