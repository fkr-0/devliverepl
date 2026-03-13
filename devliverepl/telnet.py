"""Telnet server wrapper for ptpython REPL."""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Optional

try:
    from ptpython.repl import embed as ptpython_embed
    from prompt_toolkit.contrib.telnet.server import TelnetServer as PtTelnetServer
    PTPTYTHON_AVAILABLE = True
except ImportError:
    PTPTYTHON_AVAILABLE = False
    PtTelnetServer = None
    ptpython_embed = None


logger = logging.getLogger(__name__)


class TelnetServer:
    """Telnet server wrapper for ptpython REPL.

    This class wraps prompt_toolkit's TelnetServer to provide
    a cleaner interface and better error handling.
    """

    def __init__(
        self,
        port: int = 8022,
        host: str = "127.0.0.1",
        namespace_getter: Optional[Callable[[], dict]] = None,
    ) -> None:
        """Initialize the telnet server.

        Args:
            port: Port to listen on.
            host: Host address to bind to.
            namespace_getter: Function that returns REPL namespace dict.
        """
        self.port = port
        self.host = host
        self._namespace_getter = namespace_getter
        self._server: Optional[PtTelnetServer] = None
        self._running = False

    def get_bind_address(self) -> tuple[str, int]:
        """Get the server's bind address.

        Returns:
            Tuple of (host, port).
        """
        return (self.host, self.port)

    def is_running(self) -> bool:
        """Check if the server is currently running.

        Returns:
            True if running, False otherwise.
        """
        return self._running

    async def start(self) -> None:
        """Start the telnet server.

        Raises:
            OSError: If the port is already in use.
        """
        if not PTPTYTHON_AVAILABLE:
            raise ImportError(
                "ptpython is required. Install with: pip install ptpython"
            )

        if self._running:
            logger.warning("TelnetServer already running")
            return

        async def interact(connection=None) -> Awaitable[None]:
            """Handle telnet connection."""
            # Get namespace from getter or use empty dict
            if self._namespace_getter:
                namespace = self._namespace_getter()
            else:
                namespace = {}

            # Run ptpython REPL
            await ptpython_embed(
                return_asyncio_coroutine=True,
                globals=namespace,
            )

        self._server = PtTelnetServer(
            interact=interact,
            port=self.port,
            host=self.host,
        )

        try:
            self._server.start()
            self._running = True
            logger.info(f"TelnetServer started on {self.host}:{self.port}")
        except OSError as e:
            logger.error(f"Failed to start TelnetServer: {e}")
            self._server = None
            raise

    async def stop(self) -> None:
        """Stop the telnet server."""
        if not self._running:
            return

        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        self._running = False
        logger.info("TelnetServer stopped")
