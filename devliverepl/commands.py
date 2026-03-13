"""Interactive REPL % commands."""

from __future__ import annotations

import sys
import importlib
import threading
from typing import Callable, Optional

from devliverepl.registry import get_global_registry
from devliverepl.capture import get_context_registry


class CommandRegistry:
    """Registry for REPL % commands."""

    def __init__(self) -> None:
        self._commands: dict[str, tuple[Callable, str]] = {}
        self._lock = threading.RLock()

    def register(self, name: str, func: Callable, help_text: str = "") -> None:
        """Register a command.

        Args:
            name: Command name (without % prefix).
            func: Command function.
            help_text: Help text for the command.
        """
        with self._lock:
            self._commands[name] = (func, help_text)

    def get(self, name: str) -> Optional[Callable]:
        """Get a command function by name.

        Args:
            name: Command name.

        Returns:
            Command function, or None if not found.
        """
        with self._lock:
            entry = self._commands.get(name)
            return entry[0] if entry else None

    def list_names(self) -> list[str]:
        """List all registered command names.

        Returns:
            List of command names.
        """
        with self._lock:
            return list(self._commands.keys())

    def get_help(self, name: str) -> str:
        """Get help text for a command.

        Args:
            name: Command name.

        Returns:
            Help text, or empty string if not found.
        """
        with self._lock:
            entry = self._commands.get(name)
            return entry[1] if entry else ""

    def get_help_all(self) -> str:
        """Generate help text for all commands.

        Returns:
            Formatted help text.
        """
        with self._lock:
            lines = ["Available commands:"]
            for name, (_, help_text) in sorted(self._commands.items()):
                if help_text:
                    lines.append(f"  %{name:<15} — {help_text}")
                else:
                    lines.append(f"  %{name}")
            return "\n".join(lines)


# Global command registry
_global_registry = CommandRegistry()


def register_command(
    name: str,
    help_text: str = "",
) -> Callable[[Callable], Callable]:
    """Decorator to register a REPL command.

    Args:
        name: Command name.
        help_text: Help text for the command.

    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        _global_registry.register(name, func, help_text)
        return func
    return decorator


def get_command_registry() -> CommandRegistry:
    """Get the global command registry.

    Returns:
        The global CommandRegistry instance.
    """
    return _global_registry


# ============================================================================
# Built-in commands
# ============================================================================

@register_command("ls", "List discovered modules and exposed objects")
def _cmd_ls() -> str:
    """List discovered modules and exposed objects."""
    registry = get_global_registry()
    obj_names = registry.list_names()

    context_reg = get_context_registry()
    context = context_reg.get_latest()

    lines = []

    if obj_names:
        lines.append("Exposed objects:")
        for name in sorted(obj_names):
            obj = registry.get(name)
            obj_type = type(obj).__name__
            lines.append(f"  {name} ({obj_type})")

    if context and context.locals:
        lines.append("\nCaptured locals:")
        for name, value in sorted(context.locals.items()):
            type_name = type(value).__name__
            lines.append(f"  {name} ({type_name})")

    if context and context.globals:
        # Show key globals
        important_globals = {k: v for k, v in context.globals.items()
                            if not k.startswith("__")}
        if important_globals:
            lines.append("\nKey globals:")
            for name in sorted(important_globals.keys())[:10]:
                lines.append(f"  {name}")

    return "\n".join(lines) if lines else "No objects or context available."


@register_command("import", "Import a module by name")
def _cmd_import(name: str) -> str:
    """Import a module by name.

    Args:
        name: Module name to import.

    Returns:
        Result message.
    """
    try:
        module = importlib.import_module(name)
        # Add to caller's globals
        frame = sys._getframe(2)  # Skip _cmd_import and wrapper
        if frame is not None:
            frame.f_globals[name] = module
        return f"Imported {name}"
    except ImportError as e:
        return f"Failed to import {name}: {e}"
    except Exception as e:
        return f"Error importing {name}: {e}"


@register_command("where", "Show where an object was defined")
def _cmd_where(name: str) -> str:
    """Show where an object was defined.

    Args:
        name: Object name to look up.

    Returns:
        Location info.
    """
    registry = get_global_registry()
    obj = registry.get(name)

    if obj is None:
        context_reg = get_context_registry()
        context = context_reg.get_latest()
        if context:
            obj = context.locals.get(name) or context.globals.get(name)

    if obj is None:
        return f"Object '{name}' not found"

    # Get module and file info
    module = getattr(obj, "__module__", None)
    qualname = getattr(obj, "__qualname__", None)

    if hasattr(obj, "__code__"):
        # Function/method
        filename = getattr(obj.__code__, "co_filename", "<unknown>")
        lineno = getattr(obj.__code__, "co_firstlineno", "?")
        return f"{name} defined at {filename}:{lineno}"
    elif hasattr(obj, "__class__"):
        # Class instance
        cls = obj.__class__
        module = cls.__module__
        return f"{name} is instance of {cls.__name__} from module {module}"
    else:
        return f"{name}: {type(obj).__name__}"


@register_command("env", "Show captured environment summary")
def _cmd_env() -> str:
    """Show captured environment summary."""
    context_reg = get_context_registry()
    context = context_reg.get_latest()

    if not context:
        return "No context captured"

    lines = [
        f"Captured from: {context.function} at {context.filename}:{context.lineno}",
        f"Locals: {len(context.locals)} items",
        f"Globals: {len(context.globals)} items",
    ]

    if context.locals:
        lines.append("\nLocal variables:")
        for name in sorted(context.locals.keys())[:15]:
            lines.append(f"  {name}")
        if len(context.locals) > 15:
            lines.append(f"  ... and {len(context.locals) - 15} more")

    return "\n".join(lines)


@register_command("help", "Show this help message")
def _cmd_help(command: Optional[str] = None) -> str:
    """Show help for commands.

    Args:
        command: Optional command name for detailed help.

    Returns:
        Help text.
    """
    if command:
        func = _global_registry.get(command)
        if func is None:
            return f"Unknown command: {command}"
        help_text = _global_registry.get_help(command)
        doc = getattr(func, "__doc__", "")
        return f"%{command}\n{help_text}\n{doc}"
    else:
        return _global_registry.get_help_all()


# Export command functions for use in REPL
def get_commands_dict() -> dict[str, Callable]:
    """Get all commands as a dict for REPL namespace.

    Returns:
        Dict mapping command names to functions.
    """
    return {name: _global_registry.get(name)
            for name in _global_registry.list_names()
            if _global_registry.get(name) is not None}
