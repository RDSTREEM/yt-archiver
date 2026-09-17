from dataclasses import dataclass
from config import CHUNK_SIZE


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


"""
Manifest Format


manifest.json

version: ...
c_size: ...
files: {
    x: [start, end]
}


"""


class Manifest:
    def __init__(self, files_path) -> None:
        data: bytes = b""
        chunk = 0
        file_map = {}
        for path in files_path:
            start = chunk
            with open(path, mode="rb+") as file:
                data += file.read()
                index = 0
                while index < len(data):
                    chunk += 1
                    index += CHUNK_SIZE
            file_map[path] = (start, chunk + 1)

        self.data = data
        self.num_chunks = chunk
        self.file_map = file_map

    def generate_manifest(self):
        pass
