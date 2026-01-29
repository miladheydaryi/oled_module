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

NTYPE_CON_STATE_SET = 1
NTYPE_CON_STATE = 2
NTYPE_CON_STATE_GET = 3
NTYPE_PDU_STATE_GET = 4
NTYPE_PDU_STATE = 5
NTYPE_PDU_CONFIG_SET = 6


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


# --- bcpdu Get State (Python) ---
def bcpdu_get_channel_state(channel: int) -> Message:

    # Bytearray mit 0x21 auffüllen
    byte_array_max = bytearray([0x21] * 16)

    # UTF-8 Bytes kopieren
    byte_array = channel.encode("utf-8")
    byte_array_max[:len(byte_array)] = byte_array

    # Big-Endian: jeweils 2 Bytes zu einem 16-bit Wert
    params = []
    for i in range(0, 16, 2):
        hi = byte_array_max[i]
        lo = byte_array_max[i + 1]
        value = (hi << 8) | lo
        params.append(value)

    # 0 + NTYPE + 8 Parameter
    return Message(params=[0, NTYPE_CON_STATE_GET, *params])


def bcpdu_set_channel_state(channel: int, state: str) -> Message:
    """Set channel state.

    Args:
        channel: Channel number (1-16)
        state: State value ("off", "KL30", "KL15")
    """
    # Map state strings to values
    state_map = {"off": 0, "KL30": 1, "KL15": 3}
    state_value = state_map.get(state, 0)

    # Message format: $0,1,channel,state*checksum
    return Message(params=[0, NTYPE_CON_STATE_SET, channel, state_value])
