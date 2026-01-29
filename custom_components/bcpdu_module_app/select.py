"""Select platform for BCPDU Module App."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant

from .api import BcpduModuleApi

OPTIONS = ["off", "KL30", "KL15"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the select platform."""
    api: BcpduModuleApi = entry.runtime_data

    # Create 16 channel selectors
    entities = [BcpduChannelSelect(api, channel) for channel in range(0, 16)]
    async_add_entities(entities)


class BcpduChannelSelect(SelectEntity):
    """Select entity for BCPDU channel control."""

    _attr_options = OPTIONS
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, api: BcpduModuleApi, channel: int) -> None:
        """Initialize the select entity."""
        self._api = api
        self._channel = channel
        self._attr_name = f"Channel {channel}"
        self._attr_unique_id = f"bcpdu_channel_{channel}"
        self._attr_current_option = "off"

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        await self._api.async_set_channel(self._channel, option)
        self._attr_current_option = option
        self.async_write_ha_state()
