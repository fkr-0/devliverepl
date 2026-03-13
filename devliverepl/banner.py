"""Banner generation for REPL connection."""

from __future__ import annotations

import dataclasses
import os
from typing import Callable, Optional

from devliverepl.config import get_config
from devliverepl.capture import CapturedContext


@dataclasses.dataclass
class BannerConfig:
    """Configuration for banner rendering.

    Attributes:
        show_memory: Include memory usage in rich banner.
        show_threads: Include thread count in rich banner.
        show_uptime: Include process uptime in rich banner.
        show_modules: Include discovered modules in rich banner.
    """
    show_memory: bool = True
    show_threads: bool = True
    show_uptime: bool = True
    show_modules: bool = True


def _get_process_info() -> dict[str, str]:
    """Get process information for rich banner.

    Returns:
        Dictionary with process info strings.
    """
    info = {
        "pid": str(os.getpid()),
        "memory": "N/A",
        "threads": "N/A",
        "uptime": "N/A",
    }

    try:
        import psutil
        process = psutil.Process()

        info["memory"] = f"{process.memory_info().rss / 1024 / 1024:.0f} MB"
        info["threads"] = str(process.num_threads())
    except ImportError:
        pass

    return info


def generate_banner(
    level: str = "rich",
    context: Optional[CapturedContext] = None,
    banner_config: Optional[BannerConfig] = None,
) -> Callable[[], str]:
    """Generate a banner function for the given level.

    Args:
        level: Banner level (minimal|rich|custom).
        context: Optional captured context for display.
        banner_config: Optional banner rendering config.

    Returns:
        Function that generates the banner string.
    """
    if level == "custom":
        config = get_config()
        if config.banner_func is not None:
            return config.banner_func
        # Fall through to rich if no custom function

    if level == "minimal":
        return _minimal_banner
    else:  # rich
        return lambda: _rich_banner(context, banner_config)


def _minimal_banner() -> str:
    """Generate minimal banner."""
    config = get_config()
    return f"""
devliverepl — PID {os.getpid()} — telnet {config.host} {config.port}
Type %help for commands, exit() or Ctrl-D to disconnect.
"""


def _rich_banner(
    context: Optional[CapturedContext] = None,
    banner_config: Optional[BannerConfig] = None,
) -> str:
    """Generate rich banner with process info and context."""
    config = get_config()
    bc = banner_config or BannerConfig()

    proc_info = _get_process_info()

    lines = [
        "╭─────────────────────────────────────────────────────────────╮",
        f"│  devliverepl v0.1.0 — Process #{proc_info['pid']:<25} │",
    ]

    if bc.show_memory or bc.show_threads:
        info_parts = []
        if bc.show_memory:
            info_parts.append(f"Memory: {proc_info['memory']}")
        if bc.show_threads:
            info_parts.append(f"Threads: {proc_info['threads']}")
        if info_parts:
            lines.append(f"│  {', '.join(info_parts):<57} │")

    lines.append("╰─────────────────────────────────────────────────────────────╯")

    # Context summary
    if context and context.locals:
        local_names = list(context.locals.keys())[:5]
        if local_names:
            lines.append("")
            lines.append("🔧 Captured from detach() call site:")
            for name in local_names:
                lines.append(f"   • {name}")
            if len(context.locals) > 5:
                lines.append(f"   ... and {len(context.locals) - 5} more")

    # Commands help
    lines.append("")
    lines.append("Type %help for commands, exit() or Ctrl-D to disconnect.")

    return "\n".join(lines)


# Custom banner override
_custom_banner_func: Optional[Callable[[], str]] = None


def set_custom_banner(func: Callable[[], str]) -> None:
    """Set a custom banner function.

    Args:
        func: Function that returns banner string.
    """
    global _custom_banner_func
    _custom_banner_func = func


def get_custom_banner() -> Optional[Callable[[], str]]:
    """Get the custom banner function if set.

    Returns:
        Custom banner function, or None.
    """
    return _custom_banner_func
