import zlib

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