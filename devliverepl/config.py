"""Configuration management for devliverepl."""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ReplConfig:
    """Configuration for devliverepl.

    Attributes:
        port: Telnet port to listen on.
        host: Host address to bind to.
        banner_level: Banner verbosity level (minimal|rich|custom).
        banner_func: Custom banner function.
        auto_import_exposed: Auto-import exposed objects into REPL namespace.
        log_connections: Log telnet connections.
        log_commands: Log REPL commands.
        shutdown_timeout: Seconds to wait for graceful shutdown.
        enable_atexit: Register atexit handler for cleanup.
        discover_local_modules: Auto-discover local modules.
        module_ignore_patterns: Module name patterns to ignore.
    """
    port: int = 8022
    host: str = "127.0.0.1"
    banner_level: str = "rich"
    banner_func: Optional[Callable[[], str]] = None
    auto_import_exposed: bool = True
    log_connections: bool = True
    log_commands: bool = False
    shutdown_timeout: float = 30.0
    enable_atexit: bool = True
    discover_local_modules: bool = True
    module_ignore_patterns: list[str] = field(default_factory=lambda: [
        "test_", "tests.", "__pycache__",
    ])


# Global config instance
_config = ReplConfig()


def configure(**kwargs) -> None:
    """Update configuration.

    Args:
        **kwargs: Configuration values to update.

    Raises:
        ValueError: If an unknown config option is provided.
    """
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown config option: {key}")


def get_config() -> ReplConfig:
    """Get current configuration.

    Returns:
        The current ReplConfig instance.
    """
    return _config
