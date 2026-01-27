"""api for the breuer_app integration."""

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class OledModuleApi:
    """API for communicating with the OLED module."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the OLED module API.

        Args:
            host: IP address or hostname of the OLED module.
            port: TCP port of the OLED module.
        """
        self._host = host
        self._port = port

    async def async_send_text(self, text: str) -> None:
        """Send text to the OLED module."""
        _reader, writer = await asyncio.open_connection(
            self._host,
            self._port,
        )

        writer.write(f"{text}\n".encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()
