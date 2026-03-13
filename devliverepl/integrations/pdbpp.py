"""pdb++ (pdbpp) integration."""

from devliverepl.capture import get_current_context
import sys


def attach(frame=None):
    """Attach pdb++ debugger with captured context.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.

    Raises:
        ImportError: If pdbpp is not installed.

    Example:
        >>> from devliverepl.integrations.pdbpp import attach
        >>> attach()
    """
    try:
        import pdbpp
    except ImportError:
        print("pdb++ is not installed.")
        print("Install with: pip install pdbpp")
        print("Or with uv: uv add pdbpp")
        return

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        frame = sys._getframe(1)

    pdbpp.set_trace(frame=frame)


# Check availability
try:
    import pdbpp
    available = True
except ImportError:
    available = False

__all__ = ["attach", "available"]
