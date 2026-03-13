"""Web-PDB (web-based remote debugger) integration."""

from devliverepl.capture import get_current_context
import sys


def attach(frame=None, port=5555):
    """Attach Web-PDB debugger with captured context.

    Opens a web-based debugger interface in your browser.

    Args:
        frame: Optional frame to debug. Defaults to captured call site.
        port: Port for the web debugger interface.

    Raises:
        ImportError: If web-pdb is not installed.

    Example:
        >>> from devliverepl.integrations.webpdb import attach
        >>> attach()  # Then open http://localhost:5555 in browser
    """
    try:
        import web_pdb
    except ImportError:
        print("Web-PDB is not installed.")
        print("Install with: pip install web-pdb")
        print("Or with uv: uv add web-pdb")
        return

    if frame is None:
        ctx = get_current_context()
        if ctx and ctx.frame:
            frame = ctx.frame

    if frame is None:
        frame = sys._getframe(1)

    web_pdb.set_trace(frame=frame, port=port)


# Check availability
try:
    import web_pdb
    available = True
except ImportError:
    available = False

__all__ = ["attach", "available"]
