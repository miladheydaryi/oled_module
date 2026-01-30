from __future__ import annotations

import asyncio
import logging
from typing import Optional
from .message import Message

_LOGGER = logging.getLogger(__name__)

class AsyncTcpClient:
    """Generic async TCP client."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self._writer is not None:
            return

        _LOGGER.debug("Connecting to %s:%s", self._host, self._port)
        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._port,
        )

    async def disconnect(self) -> None:
        if self._writer is None:
            return

        _LOGGER.debug("Disconnecting from %s:%s", self._host, self._port)
        self._writer.close()
        await self._writer.wait_closed()

        self._reader = None
        self._writer = None

    async def send(self, message: Message, read_response: bool = False) -> bytes | None:
        async with self._lock:
            if self._writer is None:
                await self.connect()

            try:
                assert self._writer is not None
                self._writer.write(message.to_byte())
                await self._writer.drain()

                if read_response:
                    assert self._reader is not None
                    return await self._reader.read(1024)

                return None

            except (ConnectionError, OSError):
                _LOGGER.warning("Connection lost, reconnecting...")
                await self.disconnect()
                await self.connect()

                assert self._writer is not None
                self._writer.write(message.to_byte())
                await self._writer.drain()

                if read_response:
                    assert self._reader is not None
                    return await self._reader.read(1024)

                return None