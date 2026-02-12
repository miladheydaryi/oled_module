"""Init for the dsrc_module_app integration."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
import logging
from dataclasses import dataclass, field

from asyncio_mqtt import Client, MqttError

from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOPIC,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DEFAULT_HOST, DEFAULT_PORT, DOMAIN, SIGNAL_PAYLOAD_UPDATED

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.SENSOR]

@dataclass
class DsrcRuntime:
    """Holds runtime MQTT objects for a config entry."""

    client: Client
    listener_task: asyncio.Task[None]
    last_values: dict[str, str] = field(default_factory=dict)
    last_topic: str | None = None
    last_received: datetime | None = None


async def _mqtt_listener(
    hass: HomeAssistant, entry_id: str, client: Client
) -> None:
    """Listen for MQTT messages and store latest JSON key values."""
    async with client.unfiltered_messages() as messages:
        async for message in messages:
            payload = message.payload.decode(errors="replace")
            runtime: DsrcRuntime | None = hass.data.get(DOMAIN, {}).get(entry_id)
            if runtime is None:
                continue
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            if runtime.last_values is None:
                runtime.last_values = {}
            for key, value in data.items():
                runtime.last_values[str(key)] = str(value)
            runtime.last_topic = message.topic
            runtime.last_received = datetime.now(timezone.utc)
            async_dispatcher_send(hass, SIGNAL_PAYLOAD_UPDATED, entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DSRC module from config entry."""
    host = entry.data.get(CONF_HOST, DEFAULT_HOST)
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    topic = entry.data.get(CONF_TOPIC)

    client = Client(
        hostname=host,
        port=port,
        username=username,
        password=password,
    )

    try:
        await client.connect()
        if topic:
            await client.subscribe(topic)
    except MqttError as err:
        _LOGGER.warning("Could not connect to MQTT at %s:%s: %s", host, port, err)
        return False

    listener_task = hass.async_create_task(_mqtt_listener(hass, entry.entry_id, client))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = DsrcRuntime(
        client=client, listener_task=listener_task, last_values={}
    )

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)

    unsub = hass.data.get(DOMAIN, {}).get("_unsub", {}).pop(entry.entry_id, None)
    if unsub is not None:
        unsub()

    runtime: DsrcRuntime | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is None:
        return True

    runtime.listener_task.cancel()
    try:
        await runtime.listener_task
    except asyncio.CancelledError:
        pass

    try:
        await runtime.client.disconnect()
    except MqttError as err:
        _LOGGER.debug("Error disconnecting MQTT client: %s", err)

    return True
