from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from typing import List

# --- Protocol-Konstanten ---
TMCP_START = '$'
TMCP_END = '*'
TMCP_NLCR = '\r'
TMCP_NLLF = '\n'
TMCP_SEPARATOR = ','

TMCP_PARAM_MAX = 15

NTYPE_OLED_SHOW_TEXT = 12
NTYPE_OLED_CLEAR_TEXT = 11


# --- CRC Checksum ---
class CrcChecksum:
    def __init__(self, buffer: str | None = None, checksum: int | None = None):
        self.checksumval = 0
        if buffer is not None:
            data = buffer.encode()  # entspricht Java: buffer.getBytes()
            self.checksumval = zlib.crc32(data) & 0xFFFFFFFF
        elif checksum is not None:
            self.checksumval = checksum & 0xFFFFFFFF

    def to_str(self) -> str:
        return f"{self.checksumval:08x}"


# --- Message ---
@dataclass
class Message:
    params: List[int] = field(default_factory=list)

    def __post_init__(self):
        self.params = self.params[:TMCP_PARAM_MAX]

    def to_str(self) -> str:
        payload = TMCP_SEPARATOR.join(str(p) for p in self.params)
        checksum = CrcChecksum(payload).to_str()
        message = f"{TMCP_START}{payload}{TMCP_END}{checksum}{TMCP_NLCR}{TMCP_NLLF}"
        print(message)
        return message


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
