"""Init for the dsrc_module_app integration."""

from __future__ import annotations

import logging

from asyncio_mqtt import MqttError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOPIC,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DEFAULT_HOST, DEFAULT_PORT, DOMAIN, SIGNAL_PAYLOAD_UPDATED
from .dsrc_api import DsrcModuleApi

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.SENSOR]

type DsrcConfigEntry = ConfigEntry[DsrcModuleApi]


async def async_setup_entry(hass: HomeAssistant, entry: DsrcConfigEntry) -> bool:
    """Set up DSRC module from config entry."""

    def _notify() -> None:
        async_dispatcher_send(hass, SIGNAL_PAYLOAD_UPDATED, entry.entry_id)

    api = DsrcModuleApi(
        host=entry.data.get(CONF_HOST, DEFAULT_HOST),
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        username=entry.data.get(CONF_USERNAME),
        password=entry.data.get(CONF_PASSWORD),
        topic=entry.data.get(CONF_TOPIC),
        on_update=_notify,
    )

    try:
        await api.async_connect()
    except (MqttError, OSError):
        _LOGGER.warning(
            "Could not connect to MQTT at %s:%s.",
            entry.data.get(CONF_HOST, DEFAULT_HOST),
            entry.data.get(CONF_PORT, DEFAULT_PORT),
        )
        return False

    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DsrcConfigEntry) -> bool:
    """Unload a config entry."""
    api: DsrcModuleApi = entry.runtime_data
    await api.async_disconnect()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
