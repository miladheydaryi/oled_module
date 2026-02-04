"""API for the oled_module_app integration."""

from __future__ import annotations

import asyncio
import logging
from .const import DEFAULT_HOST,DEFAULT_PORT
from .socket_client import AsyncTcpClient
from .oled import oled_show_text,oled_clear_text

_LOGGER = logging.getLogger(__name__)


class OledModuleApi:
    """API for communicating with the OLED module via TCP socket."""

    def __init__(
            self,
            host: str = DEFAULT_HOST,
            port: int = DEFAULT_PORT) -> None:
        """Initialize the OLED module API."""
        self._client = AsyncTcpClient(host, port)

    async def async_connect(self) -> None:
        """Connect to the OLED module."""
        await self._client.connect()

    async def async_disconnect(self) -> None:
        """Disconnect from the OLED module."""
        await self._client.disconnect()

    async def async_send_text(self, text: str) -> None:
        """Send text to the OLED module."""
        payload = oled_show_text(text)
        _LOGGER.info("Sending text: %s", text)
        await self._client.send(payload)

    async def async_clear_text(self) -> None:
        """Clear text from the OLED module."""
        payload = oled_clear_text()
        _LOGGER.info("Clearing OLED display")
        _LOGGER.info("Payload bytes: %s", payload)
        assert self._client.send(payload)
