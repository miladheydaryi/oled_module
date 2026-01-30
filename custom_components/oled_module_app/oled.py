from __future__ import annotations

from .._shared.message import Message,NTYPE_OLED_SHOW_TEXT,NTYPE_OLED_CLEAR_TEXT

def oled_show_text(text: str) -> Message:
    text = text[:16]
    byte_array_max = bytearray([0x21] * 16)
    byte_array = text.encode("utf-8")
    byte_array_max[:len(byte_array)] = byte_array
    params = []
    for i in range(0, 16, 2):
        hi = byte_array_max[i]
        lo = byte_array_max[i + 1]
        value = (hi << 8) | lo
        params.append(value)
    return Message(params=[0, NTYPE_OLED_SHOW_TEXT, *params])

def oled_clear_text() -> Message:
    """Clear text from OLED."""
    return Message(params=[0, NTYPE_OLED_CLEAR_TEXT])
