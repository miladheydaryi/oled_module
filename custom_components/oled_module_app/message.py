from dataclasses import dataclass, field
from typing import List
from .crc_checksum import CrcChecksum

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
NTYPE_OLED_SHOW_TEXT = 12
NTYPE_OLED_CLEAR_TEXT = 11

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

    def to_byte(self) -> bytes:
        # Convert to bytes (already big-endian compatible)
        return self.to_str().encode('utf-8')