"""API for the bcpdu_module_app integration."""

from __future__ import annotations

import logging
from .const import DEFAULT_HOST,DEFAULT_PORT
from .bcpdu import bcpdu_set_channel_state
from .socket_client import AsyncTcpClient

_LOGGER = logging.getLogger(__name__)

class BcpduModuleApi:
    """API for communicating with the BCPDU module via TCP socket."""

    def __init__(
            self,
            host: str = DEFAULT_HOST,
            port: int = DEFAULT_PORT) -> None:
        """Initialize the BCPDU module API."""
        self._client=AsyncTcpClient(host,port)

    async def async_connect(self) -> None:
        """Connect to the BCPDU module."""
        await self._client.connect()

    async def async_disconnect(self) -> None:
        """Disconnect from the BCPDU module."""
        await self._client.disconnect()

    async def async_set_channel(self, channel: int, state: str) -> None:
        payload = bcpdu_set_channel_state(channel, state)
        _LOGGER.debug("Setting channel %d to %s", channel, state)
        await self._client.send(payload,True)

"""
TODO: write Method for get channel and other stuff, and parse the result
"""
