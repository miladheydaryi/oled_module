# OLED Module Integration for Home Assistant

A custom Home Assistant integration for controlling an OLED display module via TCP socket connection.

## Features

- **Text Input Entity**: Enter and send custom text to the OLED display (max 16 characters)
- **Send Text Button**: Quick action button to send predefined text
- **Clear Display Button**: Clear all text from the OLED display
- **TCP Socket Communication**: Reliable connection management with automatic reconnection

## Installation

1. Copy the `custom_components/oled_module_app` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "Oled Module App" and follow the setup wizard

## Configuration

During setup, you'll be asked to provide:

- **Host**: IP address of the OLED module (default: `x.x.x.x`)
- **Port**: TCP port number (default: `10001`)

## Entities

After installation, the following entities will be available:

### Text Input: `text.oled_text`
- Enter custom text (up to 16 characters)
- Text is automatically sent to the OLED display when updated

### Button: `button.send_text_to_oled`
- Sends the predefined text "From HA" to the display
- Useful for testing or quick messages

### Button: `button.clear_oled`
- Clears all text from the OLED display

## Protocol

The integration uses a custom TCP protocol format:

```
$<param1>,<param2>,...*<checksum>\r\n
```

### Message Types
- **Show Text** (Type 12): `$0,12,<encoded_text>*<crc32>`
- **Clear Text** (Type 11): `$0,11*<crc32>`

Text is encoded as UTF-8 bytes, padded to 16 characters with `0x21`, and packed as big-endian 16-bit values.

## Example Automation

```yaml
automation:
  - alias: "Display Welcome Message"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: text.set_value
        target:
          entity_id: text.oled_text
        data:
          value: "Welcome Home!"
```

## Troubleshooting

### Connection Issues
- Verify the OLED module is powered on and connected to your network
- Check that the host and port settings are correct
- View logs in **Settings** → **System** → **Logs** for connection errors

### Text Not Displaying
- Ensure text is 16 characters or less
- Check Home Assistant logs for protocol errors
- Verify the OLED module is receiving data on the configured port

## Development

### Files Structure
```
custom_components/oled_module_app/
├── __init__.py       # Integration setup
├── api.py            # TCP socket communication
├── button.py         # Button entities
├── config_flow.py    # Configuration UI
├── const.py          # Constants
├── manifest.json     # Integration metadata
├── oled.py           # Protocol implementation
├── strings.json      # UI translations
└── text.py           # Text input entity
```

### Logging
The integration logs to `homeassistant.custom_components.oled_module_app`. Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.oled_module_app: debug
```

## License

This integration is provided as-is for personal use.
