"""Core REPL server implementation."""

from __future__ import annotations

import asyncio
import atexit
import logging
import threading
from typing import Optional

from devliverepl.config import ReplConfig, get_config, configure as _configure
from devliverepl.capture import capture_call_site, get_context_registry
from devliverepl.telnet import TelnetServer
from devliverepl.banner import generate_banner, BannerConfig
from devliverepl.commands import get_commands_dict
from devliverepl.registry import get_exposed_objects


logger = logging.getLogger(__name__)


# Global server instance (singleton pattern)
_global_server: Optional["REPLServer"] = None
_server_lock = threading.Lock()


class REPLServer:
    """Main REPL server that manages the telnet connection and event loop."""

    def __init__(self, config: Optional[ReplConfig] = None) -> None:
        """Initialize the REPL server.

        Args:
            config: Configuration. If None, uses global config.
        """
        self.config = config or get_config()
        self._telnet_server: Optional[TelnetServer] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def port(self) -> int:
        """Get the server port."""
        return self.config.port

    @property
    def host(self) -> str:
        """Get the server host."""
        return self.config.host

    def is_running(self) -> bool:
        """Check if the server is running.

        Returns:
            True if running, False otherwise.
        """
        return self._running

    def _create_namespace(self) -> dict:
        """Create the REPL namespace.

        Merges captured context, exposed objects, and commands.

        Returns:
            Dictionary for REPL globals.
        """
        namespace = {
            "__name__": "__console__",
            "__doc__": None,
        }

        # Add captured context
        context_reg = get_context_registry()
        context = context_reg.get_latest()
        if context:
            namespace.update(context.to_dict())

        # Add exposed objects
        exposed = get_exposed_objects()
        namespace.update(exposed)

        # Add commands (without % prefix for easy access)
        commands = get_commands_dict()
        namespace.update(commands)

        return namespace

    def start(self) -> None:
        """Start the REPL server in a background thread.

        Raises:
            RuntimeError: If server is already running.
        """
        if self._running:
            logger.warning("REPLServer already running")
            return

        # Create new event loop for this thread
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)

        # Create telnet server
        self._telnet_server = TelnetServer(
            port=self.config.port,
            host=self.config.host,
            namespace_getter=self._create_namespace,
        )

        # Start telnet server in event loop
        self._event_loop.create_task(self._run_server())

        # Start event loop in daemon thread
        self._thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
            name="devliverepl-eventloop",
        )
        self._thread.start()
        self._running = True

        logger.info(f"REPLServer started on {self.host}:{self.port}")

    async def _run_server(self) -> None:
        """Run the telnet server (coroutine)."""
        if self._telnet_server is None:
            return

        try:
            await self._telnet_server.start()
        except Exception as e:
            logger.error(f"Telnet server error: {e}")

    def _run_event_loop(self) -> None:
        """Run the event loop (in thread)."""
        if self._event_loop is None:
            return

        # Monkey-patch to disable signal handling in non-main thread
        def disable_signal_handler(*args, **kwargs):
            pass
        self._event_loop.add_signal_handler = disable_signal_handler

        try:
            self._event_loop.run_forever()
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            self._running = False

    def stop(self, force: bool = False) -> None:
        """Stop the REPL server.

        Args:
            force: If True, immediately close connections.
        """
        if not self._running:
            return

        logger.info("Stopping REPLServer...")

        # Stop event loop
        if self._event_loop is not None:
            if force:
                self._event_loop.call_soon_threadsafe(self._event_loop.stop)
            else:
                # Graceful shutdown - wait for connections to close
                async def graceful_stop():
                    if self._telnet_server is not None:
                        await self._telnet_server.stop()
                    self._event_loop.stop()

                self._event_loop.call_soon_threadsafe(
                    lambda: self._event_loop.create_task(graceful_stop())
                )

        # Wait for thread to finish
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=self.config.shutdown_timeout)
            if self._thread.is_alive():
                logger.warning("Thread did not stop in time")

        self._running = False
        self._thread = None
        self._telnet_server = None
        self._event_loop = None

        logger.info("REPLServer stopped")


def detach(**kwargs) -> REPLServer:
    """Detach a REPL server, capturing the calling context.

    This function captures the local and global variables from the calling
    frame, then starts (or updates) a telnet-accessible ptpython REPL.

    Args:
        **kwargs: Configuration overrides (port, host, banner_level, etc.)

    Returns:
        The REPLServer instance.

    Example:
        app_state = {"running": True}
        devliverepl.detach(port=8022)
        # Connect with: telnet localhost 8022
    """
    global _global_server

    # Apply config overrides
    if kwargs:
        _configure(**kwargs)

    # Capture call site context
    context = capture_call_site()
    context_reg = get_context_registry()
    context_reg.store("latest", context)

    # Get or create server
    with _server_lock:
        if _global_server is None or not _global_server.is_running():
            _global_server = REPLServer()
            _global_server.start()

            # Register atexit handler if enabled
            config = get_config()
            if config.enable_atexit:
                atexit.register(_atexit_shutdown)
        else:
            # Server already running, just update context
            logger.info("Context updated, existing REPL still running")

    return _global_server


def get_server() -> Optional[REPLServer]:
    """Get the current REPL server instance.

    Returns:
        The REPLServer, or None if not started.
    """
    return _global_server


def shutdown(force: bool = False) -> None:
    """Shutdown the REPL server.

    Args:
        force: If True, immediately close all connections.

    Example:
        devliverepl.shutdown()          # Graceful
        devliverepl.shutdown(force=True)  # Immediate
    """
    global _global_server

    with _server_lock:
        if _global_server is not None:
            _global_server.stop(force=force)
            _global_server = None

    # Unregister atexit handler
    try:
        atexit.unregister(_atexit_shutdown)
    except Exception:
        pass


def _atexit_shutdown() -> None:
    """Atexit handler for automatic shutdown."""
    logger.info("devliverepl shutdown via atexit")
    shutdown(force=True)
