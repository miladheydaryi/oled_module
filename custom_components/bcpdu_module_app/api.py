"""API for the bcpdu_module_app integration."""

from __future__ import annotations

import asyncio
import logging
from .const import DEFAULT_HOST,DEFAULT_PORT
from .bcpdu import Message,bcpdu_show_text,bcpdu_clear_text,bcpdu_set_channel

_LOGGER = logging.getLogger(__name__)


class BcpduModuleApi:
    """API for communicating with the BCPDU module via TCP socket."""

    def __init__(
            self,
            host: str = DEFAULT_HOST,
            port: int = DEFAULT_PORT) -> None:
        """Initialize the BCPDU module API."""
        self._host = host
        self._port = port

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    async def async_connect(self) -> None:
        """Open the socket connection if not connected."""
        if self._writer is not None:
            return

        _LOGGER.debug("Connecting to BCPDU module at %s:%s", self._host, self._port)

        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._port,
        )

    async def async_disconnect(self) -> None:
        """Close the socket connection."""
        if self._writer is None:
            return

        _LOGGER.debug("Disconnecting from BCPDU module")

        self._writer.close()
        await self._writer.wait_closed()

        self._writer = None
        self._reader = None

    async def async_send_text(self, text: str) -> None:
        """Send text to the BCPDU module."""
        async with self._lock:
            if self._writer is None:
                await self.async_connect()

            try:
                payload = encode_text_to_bcpdu_payload(bcpdu_show_text(text))
                _LOGGER.info("Sending text: %s", text)
                _LOGGER.info("Payload bytes: %s", payload)
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

    async def async_clear_text(self) -> None:
        """Clear text from the BCPDU module."""
        async with self._lock:
            if self._writer is None:
                await self.async_connect()

            try:
                payload = encode_text_to_bcpdu_payload(bcpdu_clear_text())
                _LOGGER.info("Clearing BCPDU display")
                _LOGGER.info("Payload bytes: %s", payload)
                assert self._writer is not None
                self._writer.write(payload)
                await self._writer.drain()

            except (ConnectionError, OSError):
                _LOGGER.warning("Connection lost, reconnecting...")
                await self.async_disconnect()
                await self.async_connect()

                assert self._writer is not None
                self._writer.write(payload)
                await self._writer.drain()

    async def async_set_channel(self, channel: int, state: str) -> None:
        """Set channel state."""
        async with self._lock:
            if self._writer is None:
                await self.async_connect()

            try:
                payload = encode_text_to_bcpdu_payload(bcpdu_set_channel_state(channel, state))
                _LOGGER.info("Setting channel %d to %s", channel, state)
                _LOGGER.info("Payload bytes: %s", payload)
                assert self._writer is not None
                self._writer.write(payload)
                await self._writer.drain()

            except (ConnectionError, OSError):
                _LOGGER.warning("Connection lost, reconnecting...")
                await self.async_disconnect()
                await self.async_connect()

                assert self._writer is not None
                self._writer.write(payload)
                await self._writer.drain()

def encode_text_to_bcpdu_payload(msg: Message) -> bytes:
    # Convert to bytes (already big-endian compatible)
    return msg.to_str().encode('utf-8')
