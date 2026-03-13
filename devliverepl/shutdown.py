"""Shutdown handling and cleanup management."""

from __future__ import annotations

import logging
import threading
from typing import Callable


logger = logging.getLogger(__name__)


class ShutdownManager:
    """Manage cleanup functions for graceful shutdown."""

    def __init__(self) -> None:
        self._cleanups: list[Callable] = []
        self._lock = threading.Lock()
        self._shut_down = False

    def register(self, cleanup: Callable) -> None:
        """Register a cleanup function.

        Args:
            cleanup: Function to call on shutdown.
        """
        with self._lock:
            if not self._shut_down:
                self._cleanups.append(cleanup)

    def shutdown(self) -> None:
        """Run all cleanup functions."""
        with self._lock:
            if self._shut_down:
                return
            self._shut_down = True

            cleanups = list(self._cleanups)
            self._cleanups.clear()

        logger.info(f"Running {len(cleanups)} cleanup functions...")

        for cleanup in cleanups:
            try:
                cleanup()
            except Exception as e:
                logger.error(f"Cleanup function failed: {e}")


# Global shutdown manager
_global_manager = ShutdownManager()


def register_cleanup(cleanup: Callable) -> None:
    """Register a cleanup function.

    The function will be called when shutdown() is called.

    Args:
        cleanup: Function to call on shutdown.

    Example:
        def close_db():
            db.close()
        register_cleanup(close_db)
    """
    _global_manager.register(cleanup)


def shutdown() -> None:
    """Run all registered cleanup functions."""
    _global_manager.shutdown()


def get_manager() -> ShutdownManager:
    """Get the global shutdown manager.

    Returns:
        The global ShutdownManager instance.
    """
    return _global_manager
