from __future__ import annotations

from .._shared.message import Message,NTYPE_OLED_SHOW_TEXT,NTYPE_OLED_CLEAR_TEXT

# --- oledShowText (Python) ---
def oled_show_text(text: str) -> Message:
    # max 16 Zeichen
    text = text[:16]

    # Bytearray mit 0x21 auffüllen
    byte_array_max = bytearray([0x21] * 16)

    # UTF-8 Bytes kopieren
    byte_array = text.encode("utf-8")
    byte_array_max[:len(byte_array)] = byte_array

    # Big-Endian: jeweils 2 Bytes zu einem 16-bit Wert
    params = []
    for i in range(0, 16, 2):
        hi = byte_array_max[i]
        lo = byte_array_max[i + 1]
        value = (hi << 8) | lo
        params.append(value)

    # 0 + NTYPE + 8 Parameter
    return Message(params=[0, NTYPE_OLED_SHOW_TEXT, *params])


def oled_clear_text() -> Message:
    """Clear text from OLED."""
    return Message(params=[0, NTYPE_OLED_CLEAR_TEXT])
