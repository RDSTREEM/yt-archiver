from dataclasses import dataclass
from config import CHUNK_SIZE
from dataclasses import asdict
from pathlib import Path
import json


@dataclass(frozen=True)
class ChunkInfo:
    id: str
    size: int


@dataclass(frozen=True)
class FileInfo:
    path: Path
    size: int
    sha256: str
    chunks: list[ChunkInfo]


"""
Manifest Format


manifest.json

format_version: ...
chunk_size: ...
files: {
    path: ...
    size: 
    sha256: 
    chunks: [
    {
        chunk_hash:
        size: 
    }
    ]
}


"""


@dataclass(frozen=True)
class Manifest:
    format_version: int
    chunk_size: int
    files: list[FileInfo]

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(path.name + ".tmp")

        try:
            with path.open("w", encoding="utf-8") as file:
                json.dump(
                    self.to_dict(),
                    file,
                    indent=4,
                    sort_keys=True,
                )
            temp_path.replace(path)

            file.write("\n")
        finally:
            temp_path.unlink(missing_ok=True)

    @classmethod
    def load(cls, path) -> "Manifest":
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if type(data) != dict:
            raise ValueError("Manifest should be a json file")

        version = data.get("format_version")
        chunk_size = data.get("chunk_size")
        raw_files = data.get("files")

        if type(version) is not int or version != 1:
            raise ValueError("Unsupported version")

        if type(chunk_size) is not int or chunk_size <= 0:
            raise ValueError("Unsupported chunk size")

        if not isinstance(raw_files, list):
            raise ValueError("'files' must be a list")

        for file in raw_files:
            if not isinstance(file, dict):
                raise ValueError("EAch file entry must be an object")

        return cls(
            format_version=version,
            chunk_size=chunk_size,
            files=raw_files,
        )
