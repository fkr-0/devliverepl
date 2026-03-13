"""PatDB (pattern debugger) integration."""

from devliverepl.capture import get_current_context
import sys


def attach(frame=None):
    """Attach PatDB debugger with captured context.

    PatDB allows setting breakpoints based on call patterns.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.

    Raises:
        ImportError: If PatDB is not installed.

    Example:
        >>> from devliverepl.integrations.patdb import attach
        >>> attach()
        >>> # In PatDB:
        >>> # pat.break_when('my_function')
        >>> # pat.break_when('process_*')
    """
    try:
        import patdb
    except ImportError:
        print("PatDB is not installed.")
        print("Install from: https://github.com/cosmoplan/patdb")
        print("Or with uv: uv add 'git+https://github.com/cosmoplan/patdb.git'")
        return

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        frame = sys._getframe(1)

    patdb.set_trace(frame=frame)


# Check availability
try:
    import patdb
    available = True
except ImportError:
    available = False

__all__ = ["attach", "available"]
