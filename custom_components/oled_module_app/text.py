"""Text platform for oled App."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import OledModuleApi

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the text platform."""
    api: OledModuleApi = entry.runtime_data

    async_add_entities([OledText(api)])


class OledText(TextEntity):
    """Text entity for OLED display."""

    _attr_name = "OLED Text"
    _attr_icon = "mdi:text"
    _attr_native_max = 16

    def __init__(self, api: OledModuleApi) -> None:
        """Initialize the text entity."""
        self._api = api
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        """Send text to OLED when value is set."""
        self._attr_native_value = value
        await self._api.async_send_text(value)
