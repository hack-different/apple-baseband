import dataclasses
import enum
import io
import struct


# Given the distance between 3/6 it seems this is actually a bitflag of algo / size
class QualcommHashType(enum.Enum):
    SHA2_256 = 3
    SHA2_394 = 6


@dataclasses.dataclass
class QualcommSignatureHeader:
    HEADER_FORMAT = '<LLLLLLLLLLLL'

    row_count: int  # Zero indicates mastered by ELF
    hash_type: QualcommHashType
    storage_offset: int  # Zero makes this mastered by ELF header
    memory_offset: int  # Zero makes this mastered by the ELF header
    total_size: int
    hashes_size: int
    certificate_offset: int  # 0xFFFFFFFF has special meaning
    certificate_size: int
    attestation_offset: int
    attestation_size: int
    reserved: int
    next_header_size: int

    @classmethod
    def from_bytes(cls, input_data: io.BytesIO) -> "QualcommSignatureHeader":
        data = input_data.read(struct.calcsize(cls.HEADER_FORMAT))
        return QualcommSignatureHeader(*struct.unpack_from(QualcommSignatureHeader.HEADER_FORMAT, data, 0))


class QualcommSignature:
    def __init__(self, data: bytes):
        self._data = io.BytesIO(data)
        self._header = QualcommSignatureHeader.from_bytes(self._data)
        if self._header.next_header_size > 0:
            self._extra = self._data.read(self._header.next_header_size)
        else:
            self._extra = b''

