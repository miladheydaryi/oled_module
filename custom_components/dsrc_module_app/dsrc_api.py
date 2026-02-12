"""MQTT API wrapper for dsrc_module_app."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from asyncio_mqtt import Client, MqttError

_LOGGER = logging.getLogger(__name__)


@dataclass
class DsrcRuntime:
    """Holds runtime MQTT objects for a config entry."""

    client: Client
    listener_task: asyncio.Task[None]
    last_values: dict[str, str] = field(default_factory=dict)
    last_topic: str | None = None
    last_received: datetime | None = None


class DsrcModuleApi:
    """MQTT API wrapper."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        topic: str | None,
        on_update: Callable[[], None] | None,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._topic = topic
        self._on_update = on_update
        self._runtime: DsrcRuntime | None = None

    @property
    def runtime(self) -> DsrcRuntime | None:
        return self._runtime

    async def async_connect(self) -> None:
        """Connect to MQTT and start listener."""
        client = Client(
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
        )
        await client.connect()
        if self._topic:
            await client.subscribe(self._topic)
        listener_task = asyncio.create_task(self._listen(client))
        self._runtime = DsrcRuntime(client=client, listener_task=listener_task)

    async def async_disconnect(self) -> None:
        """Stop listener and disconnect."""
        if self._runtime is None:
            return
        self._runtime.listener_task.cancel()
        try:
            await self._runtime.listener_task
        except asyncio.CancelledError:
            pass
        try:
            await self._runtime.client.disconnect()
        except MqttError as err:
            _LOGGER.debug("Error disconnecting MQTT client: %s", err)

    async def _listen(self, client: Client) -> None:
        """Listen for MQTT messages and store latest JSON key values."""
        async with client.unfiltered_messages() as messages:
            async for message in messages:
                payload = message.payload.decode(errors="replace")
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, dict):
                    continue
                if self._runtime is None:
                    continue
                for key, value in data.items():
                    self._runtime.last_values[str(key)] = str(value)
                self._runtime.last_topic = message.topic
                self._runtime.last_received = datetime.now(timezone.utc)
                if self._on_update is not None:
                    self._on_update()
