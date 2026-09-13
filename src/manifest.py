from dataclasses import dataclass


@dataclass
class ChunkInfo:
    id: str
    size: int


@dataclass
class FileInfo:
    path: str
    size: int
    chunks: list[
        str
    ]  # may change to list[ChunkInfo] if i decide to make each chunk size different
