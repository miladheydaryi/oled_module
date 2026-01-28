"""API for the breuer_app integration."""

from __future__ import annotations

import asyncio
import logging
from .const import DEFAULT_HOST,DEFAULT_PORT

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
                payload = encode_text_to_oled_payload(text)

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

MAX_OLED_TEXT_LENGTH = 16  # same as your Java code
PADDING_BYTE = 0x21        # '!' invalid/empty char
        
def encode_text_to_oled_payload(text: str) -> bytes:
    """Convert text into OLED HEX payload.

    - UTF-8 encoded
    - Max 16 bytes
    - Padded with 0x21
    - Big-endian 16-bit words (8 shorts)
    """
    if len(text) > MAX_OLED_TEXT_LENGTH:
        text = text[:MAX_OLED_TEXT_LENGTH]

    # Create padded byte array
    padded = bytearray([PADDING_BYTE] * MAX_OLED_TEXT_LENGTH)

    encoded = text.encode("utf-8")
    padded[: len(encoded)] = encoded

    # Convert to bytes (already big-endian compatible)
    return bytes(padded)
