"""devliverepl - Self-sufficient debugging REPL for running Python programs.

This package provides an always-on ptpython REPL server accessible via telnet
for live inspection and debugging of running Python applications.

Example:
    >>> import devliverepl
    >>> app_state = {"users": []}
    >>> devliverepl.detach()  # Captures app_state
    >>> # From another terminal: telnet localhost 8022
"""

from devliverepl.__version__ import __version__

# Public API
from devliverepl.core import detach, get_server, shutdown
from devliverepl.config import configure
from devliverepl.registry import expose, register

__all__ = [
    "__version__",
    "detach",
    "shutdown",
    "configure",
    "expose",
    "register",
    "get_server",
]


def _check_dependencies() -> None:
    """Check that required dependencies are available."""
    missing = []
    try:
        import ptpython
    except ImportError:
        missing.append("ptpython")
    try:
        import prompt_toolkit
    except ImportError:
        missing.append("prompt-toolkit")

    if missing:
        raise ImportError(
            f"devliverepl requires the following packages: {', '.join(missing)}\n"
            f"Install with: pip install {' '.join(missing)}\n"
            f"Or with uv: uv add {' '.join(missing)}"
        )


# Don't check dependencies on import - check when detach() is called
# This allows the package to be imported for documentation purposes
