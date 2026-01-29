"""Button platform for bcpdu App."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import BcpduConfigEntry
from .api import BcpduModuleApi

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the button platform."""
    api: BcpduConfigEntry = entry.runtime_data

    async_add_entities([
        OledSendTextButton(api),
        OledClearTextButton(api)
    ])


class OledSendTextButton(ButtonEntity):
    """Button to send text to OLED."""

    _attr_name = "Send text to OLED"
    _attr_icon = "mdi:monitor"

    def __init__(self, api: BcpduModuleApi) -> None:
        """Initialize the button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.async_send_text("From HA")


class OledClearTextButton(ButtonEntity):
    """Button to clear text from OLED."""

    _attr_name = "Clear OLED"
    _attr_icon = "mdi:monitor-off"

    def __init__(self, api: BcpduModuleApi) -> None:
        """Initialize the button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.async_clear_text()
