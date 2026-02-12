"""Config flow for the dsrc_module_app integration."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import voluptuous as vol
from asyncio_mqtt import Client, MqttError

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TOPIC,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_HOST, DEFAULT_PORT, DISCOVERY_TIMEOUT_SECONDS, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)

STEP_TOPIC_DATA_SCHEMA = vol.Schema({})


def _format_payload_label(topic: str, payload: bytes) -> str:
    """Build a topic label that includes JSON key/value pairs when possible."""
    text = payload.decode(errors="replace").strip()
    if not text:
        return topic

    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return topic

    if not isinstance(obj, dict):
        return topic

    pairs = [f"{key}={value}" for key, value in obj.items()]
    return f"{topic} ({', '.join(pairs)})"


async def _discover_topics(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, str]:
    """Connect to MQTT and discover topics within a time window."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)

    topics: dict[str, bytes] = {}
    loop = asyncio.get_running_loop()
    deadline = loop.time() + DISCOVERY_TIMEOUT_SECONDS

    try:
        async with Client(
            hostname=host,
            port=port,
            username=username,
            password=password,
        ) as client:
            async with client.unfiltered_messages() as messages:
                await client.subscribe("#")
                while True:
                    remaining = deadline - loop.time()
                    if remaining <= 0:
                        break
                    try:
                        message = await asyncio.wait_for(
                            messages.__anext__(), timeout=remaining
                        )
                    except asyncio.TimeoutError:
                        break
                    topics[message.topic] = message.payload
    except MqttError as err:
        raise CannotConnect from err

    labels: dict[str, str] = {}
    for topic, payload in sorted(topics.items()):
        labels[topic] = _format_payload_label(topic, payload)

    return labels


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dsrc_module_app."""

    VERSION = 1

    _broker_config: dict[str, Any] | None = None
    _topic_labels: dict[str, str] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                topic_labels = await _discover_topics(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                if not topic_labels:
                    errors["base"] = "no_topics"
                else:
                    self._broker_config = user_input
                    self._topic_labels = topic_labels
                    return await self.async_step_topic()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_topic(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user pick a topic discovered from the broker."""
        if self._broker_config is None or self._topic_labels is None:
            return await self.async_step_user()

        if user_input is not None:
            data = {**self._broker_config, **user_input}
            title = f"DSRC {self._broker_config[CONF_HOST]}"
            return self.async_create_entry(title=title, data=data)

        schema = STEP_TOPIC_DATA_SCHEMA.extend(
            {vol.Required(CONF_TOPIC): vol.In(self._topic_labels)}
        )

        return self.async_show_form(
            step_id="topic",
            data_schema=schema,
            errors={},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid authentication."""
