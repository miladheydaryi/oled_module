"""API for the breuer_app integration."""

from __future__ import annotations

import asyncio
import logging
from .const import DEFAULT_HOST,DEFAULT_PORT
from .oled import Message,oled_show_text

_LOGGER = logging.getLogger(__name__)


class OledModuleApi:
    """API for communicating with the OLED module via TCP socket."""

    def __init__(
            self,
            host: str = DEFAULT_HOST,
            port: int = DEFAULT_PORT) -> None:
        """Initialize the OLED module API."""
        self._host = host
        self._port = port

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    async def async_connect(self) -> None:
        """Open the socket connection if not connected."""
        if self._writer is not None:
            return

        _LOGGER.debug("Connecting to OLED module at %s:%s", self._host, self._port)

        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._port,
        )

    async def async_disconnect(self) -> None:
        """Close the socket connection."""
        if self._writer is None:
            return

        _LOGGER.debug("Disconnecting from OLED module")

        self._writer.close()
        await self._writer.wait_closed()

        self._writer = None
        self._reader = None

    async def async_send_text(self, text: str) -> None:
        """Send text to the OLED module."""
        async with self._lock:
            if self._writer is None:
                await self.async_connect()

            try:
                payload = encode_text_to_oled_payload(oled_show_text(text))
                _LOGGER.debug(text)
                _LOGGER.info(payload)
                assert self._writer is not None
                self._writer.write(payload)
                await self._writer.drain()

            except (ConnectionError, OSError):
                _LOGGER.warning("Connection lost, reconnecting...")
                await self.async_disconnect()
                await self.async_connect()

                assert self._writer is not None
                self._writer.write(f"{text}\n".encode())
                await self._writer.drain()
        
def encode_text_to_oled_payload(msg: Message) -> bytes:

    # Convert to bytes (already big-endian compatible)
    return bytes(msg.to_str())
