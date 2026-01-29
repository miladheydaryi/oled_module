"""Init for the bcpdu_module_app integration."""

from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .api import BcpduModuleApi
from .const import DEFAULT_HOST,DEFAULT_PORT

_PLATFORMS: list[Platform] = [ Platform.SELECT]
_LOGGER = logging.getLogger(__name__)
type BcpduConfigEntry = ConfigEntry[BcpduModuleApi]

async def async_setup_entry(hass: HomeAssistant, entry: BcpduConfigEntry) -> bool:
    """Set up Bcpdu module from config entry."""
    api = BcpduModuleApi(
        host=entry.data.get(CONF_HOST,DEFAULT_HOST),
        port=entry.data.get(CONF_PORT,DEFAULT_PORT),
    )

    try:
        await api.async_connect()
    except ConnectionRefusedError:
        _LOGGER.warning(
            "Could not connect to BCPDU at %s:%s. Will retry when sending text.",
            api._host,
            api._port,
        )

    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BcpduConfigEntry) -> bool:
    """Unload a config entry."""
    api: BcpduModuleApi = entry.runtime_data
    await api.async_disconnect()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
