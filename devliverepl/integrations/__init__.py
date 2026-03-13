"""Debugger integrations for devliverepl.

Provides unified access to multiple Python debuggers with captured
call-site context from devliverepl.

Example:
    >>> from devliverepl.integrations import get_best_debugger
    >>> best = get_best_debugger()
    >>> print(f"Best debugger: {best}")
"""

from __future__ import annotations

from devliverepl.integrations import pdb
from devliverepl.capture import get_current_context


# Priority order for debuggers (best first)
_DEBUGGER_PRIORITY = [
    ("pudb", lambda: __import__("pudb")),
    ("pdbpp", lambda: __import__("pdbpp")),
    ("ipdb", lambda: __import__("ipdb")),
    ("patdb", lambda: __import__("patdb")),
    ("webpdb", lambda: __import__("web_pdb")),
    ("pdb", lambda: __import__("pdb")),  # Always available
]


def get_available_debuggers() -> list[str]:
    """Get list of available debuggers.

    Returns:
        List of debugger names that are installed.
    """
    available = []

    # pdb is always available
    available.append("pdb")

    # Check optional debuggers
    optional_checks = [
        ("pudb", lambda: __import__("pudb")),
        ("ipdb", lambda: __import__("ipdb")),
        ("pdbpp", lambda: __import__("pdbpp")),
        ("patdb", lambda: __import__("patdb")),
        ("webpdb", lambda: __import__("web_pdb")),
    ]

    for name, check in optional_checks:
        try:
            check()
            available.append(name)
        except ImportError:
            pass

    return available


def get_best_debugger() -> str:
    """Get the name of the best available debugger.

    Returns:
        Debugger name (pudb, ipdb, pdbpp, patdb, webpdb, or pdb).
    """
    for name, check in _DEBUGGER_PRIORITY:
        try:
            check()
            return name
        except ImportError:
            continue
    return "pdb"


def get_debugger(name: str):
    """Get a debugger attach function by name.

    Args:
        name: Debugger name (pdb, pudb, ipdb, pdbpp, patdb, webpdb).

    Returns:
        Attach function, or None if not available.

    Example:
        >>> attach = get_debugger("pudb")
        >>> if attach:
        ...     attach()
    """
    if name == "pdb":
        return pdb.attach

    # Lazy load optional debuggers
    try:
        if name == "pudb":
            from devliverepl.integrations import pudb
            return pudb.attach
        elif name == "ipdb":
            from devliverepl.integrations import ipdb
            return ipdb.attach
        elif name == "pdbpp":
            from devliverepl.integrations import pdbpp
            return pdbpp.attach
        elif name == "patdb":
            from devliverepl.integrations import patdb
            return patdb.attach
        elif name == "webpdb":
            from devliverepl.integrations import webpdb
            return webpdb.attach
    except ImportError:
        return None

    return None


def attach_pdb(frame=None):
    """Attach pdb debugger.

    Wrapper for convenience - pdb is always available.
    """
    return pdb.attach(frame)


# Create a 'debug' object for REPL usage
class _DebugHelper:
    """Helper object for debugger access in REPL."""

    def __init__(self):
        self._cache = {}

    def attach(self, frame=None):
        """Attach the best available debugger."""
        best = get_best_debugger()
        func = get_debugger(best)
        if func:
            print(f"Attaching {best}...")
            return func(frame)
        else:
            print("No debugger available")
            return None

    def pdb(self, frame=None):
        """Attach pdb."""
        return pdb.attach(frame)

    def pudb(self, frame=None):
        """Attach PuDB."""
        try:
            from devliverepl.integrations import pudb
            return pudb.attach(frame)
        except ImportError:
            print("PuDB not installed. Install with: pip install pudb")
            return None

    def ipdb(self, frame=None):
        """Attach ipdb."""
        try:
            from devliverepl.integrations import ipdb
            return ipdb.attach(frame)
        except ImportError:
            print("ipdb not installed. Install with: pip install ipdb")
            return None

    def pdbpp(self, frame=None):
        """Attach pdb++."""
        try:
            from devliverepl.integrations import pdbpp
            return pdbpp.attach(frame)
        except ImportError:
            print("pdb++ not installed. Install with: pip install pdbpp")
            return None

    def patdb(self, frame=None):
        """Attach PatDB."""
        try:
            from devliverepl.integrations import patdb
            return patdb.attach(frame)
        except ImportError:
            print("PatDB not installed.")
            return None

    def web(self, frame=None):
        """Attach Web-PDB."""
        try:
            from devliverepl.integrations import webpdb
            return webpdb.attach(frame)
        except ImportError:
            print("Web-PDB not installed. Install with: pip install web-pdb")
            return None

    def list_available(self):
        """List available debuggers."""
        available = get_available_debuggers()
        best = get_best_debugger()

        lines = [f"Available debuggers:"]
        for name in ["pudb", "pdbpp", "ipdb", "patdb", "webpdb", "pdb"]:
            if name in available:
                marker = "✓" if name == best else "✓"
                lines.append(f"  {marker} {name}")
            else:
                lines.append(f"  ✗ {name} (not installed)")

        lines.append(f"\nBest available: {best}")
        return "\n".join(lines)

    def __repr__(self):
        return "<debug helper: use debug.attach(), debug.pdb(), etc.>"


# Singleton instance for REPL
_debug = _DebugHelper()


def get_debug_helper() -> _DebugHelper:
    """Get the debug helper object for REPL.

    Returns:
        _DebugHelper instance.
    """
    return _debug


__all__ = [
    "get_available_debuggers",
    "get_best_debugger",
    "get_debugger",
    "attach_pdb",
    "get_debug_helper",
]
