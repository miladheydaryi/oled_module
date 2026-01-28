"""Init for the breuer_app integration."""

from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import OledModuleApi
from .const import DEFAULT_HOST,DEFAULT_PORT

_PLATFORMS: list[Platform] = [Platform.BUTTON]
_LOGGER = logging.getLogger(__name__)
type BreuerConfigEntry = ConfigEntry[OledModuleApi]

async def async_setup_entry(hass: HomeAssistant, entry: BreuerConfigEntry) -> bool:
    """Set up OLED module from config entry."""
    api = OledModuleApi(
        host=entry.data.get(CONF_HOST,DEFAULT_HOST),
        port=entry.data.get(CONF_PORT,DEFAULT_PORT),
    )

    try:
        await api.async_connect()
    except ConnectionRefusedError:
        _LOGGER.warning(
            "Could not connect to OLED at %s:%s. Will retry when sending text.",
            api._host,
            api._port,
        )

    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BreuerConfigEntry) -> bool:
    """Unload a config entry."""
    api: OledModuleApi = entry.runtime_data
    await api.async_disconnect()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
