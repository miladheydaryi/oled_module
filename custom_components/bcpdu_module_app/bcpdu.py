from __future__ import annotations

from .._shared.message import Message,NTYPE_CON_STATE_SET,NTYPE_CON_STATE_GET

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
