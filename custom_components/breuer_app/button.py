"""Button platform for Breuer App."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import OledModuleApi

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the button platform."""
    api: OledModuleApi = entry.runtime_data

    async_add_entities([BreuerSendTextButton(api)])


class BreuerSendTextButton(ButtonEntity):
    """Button to send text to OLED."""

    _attr_name = "Send text to OLED"
    _attr_icon = "mdi:monitor"

    def __init__(self, api: OledModuleApi) -> None:
        """Initialize the button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.async_send_text("$0,12,18034,28525,8264,16673,8481,8481,8481,8481*4d4e28a0")
