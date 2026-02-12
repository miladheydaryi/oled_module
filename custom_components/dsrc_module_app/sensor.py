"""Sensor platform for dsrc_module_app."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_PAYLOAD_UPDATED
from .dsrc_api import DsrcModuleApi


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up DSRC sensor based on a config entry."""
    manager = DsrcSensorManager(hass, entry, async_add_entities)
    await manager.async_setup()


class DsrcSensorManager:
    """Create and update sensors for each JSON key."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.async_add_entities = async_add_entities
        self._entities: dict[str, DsrcKeySensor] = {}
        self._unsub_dispatcher = None

    @property
    def _runtime(self) -> object | None:
        api: DsrcModuleApi = self.entry.runtime_data
        return api.runtime if api is not None else None

    async def async_setup(self) -> None:
        """Register dispatcher and create initial sensors."""
        self._ensure_entities()

        @callback
        def _handle_update(entry_id: str) -> None:
            if entry_id == self.entry.entry_id:
                self._ensure_entities()
                for entity in self._entities.values():
                    entity.async_write_ha_state()

        self._unsub_dispatcher = async_dispatcher_connect(
            self.hass, SIGNAL_PAYLOAD_UPDATED, _handle_update
        )
        self.hass.data.setdefault(DOMAIN, {}).setdefault("_unsub", {})[
            self.entry.entry_id
        ] = self._unsub_dispatcher

    def _ensure_entities(self) -> None:
        runtime = self._runtime
        if runtime is None:
            return
        for key in runtime.last_values.keys():
            if key in self._entities:
                continue
            entity = DsrcKeySensor(self.hass, self.entry, key)
            self._entities[key] = entity
            self.async_add_entities([entity])


class DsrcKeySensor(SensorEntity):
    """Sensor that exposes a single JSON key value."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
        self.hass = hass
        self.entry = entry
        self.key = key
        self._attr_name = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def _runtime(self) -> object | None:
        api: DsrcModuleApi = self.entry.runtime_data
        return api.runtime if api is not None else None

    @property
    def native_value(self) -> str | None:
        runtime = self._runtime
        if runtime is None:
            return None
        return runtime.last_values.get(self.key)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        runtime = self._runtime
        if runtime is None:
            return None
        attrs: dict[str, str] = {}
        if runtime.last_topic:
            attrs["topic"] = runtime.last_topic
        if runtime.last_received:
            attrs["received_at"] = runtime.last_received.isoformat()
        return attrs or None
