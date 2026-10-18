from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import json
import hashlib
import re

_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass(frozen=True)
class ChunkInfo:
    id: str
    size: int


@dataclass(frozen=True)
class FileInfo:
    path: str
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
        return {
            "format_version": self.format_version,
            "chunk_size": self.chunk_size,
            "files": [
                {
                    "path": file.path,
                    "size": file.size,
                    "sha256": file.sha256,
                    "chunks": [
                        {"id": chunk.id, "size": chunk.size} for chunk in file.chunks
                    ],
                }
                for file in self.files
            ],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(path.name + ".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self.to_dict(),
                    file,
                    indent=4,
                    sort_keys=True,
                )
                file.write("\n")

            temp_path.replace(path)

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

        files = []
        seen_paths = set()  # bahahaha using what i learned in ac, dfs lets gooo

        for file in raw_files:
            if not isinstance(file, dict):
                raise ValueError("EAch file entry must be an object")

            relative_path = file.get("path")
            size = file.get("size")
            sha256 = file.get("sha256")
            raw_chunks = file.get("chunks")

            if not isinstance(relative_path, str) or not relative_path:
                raise ValueError("Invalid file path")

            if "\\" in relative_path or "\x00" in relative_path:
                raise ValueError("Unsafe path")

            path = PurePosixPath(relative_path)

            if (
                path.is_absolute()
                or any(part in ("", ".", "..") for part in relative_path.split("/"))
                or ":" in path.parts[0]
            ):
                raise ValueError("Unsafe path")

            if relative_path in seen_paths:
                raise ValueError("Duplicate file paths")

            seen_paths.add(relative_path)

            if type(size) is not int or size < 0:
                raise ValueError("Invalid file size")

            if not isinstance(sha256, str) or not _HASH_RE.fullmatch(sha256):
                raise ValueError("Invalid hash")

            if not isinstance(raw_chunks, list):
                raise ValueError("Invalid chunks list")

            chunks = []
            total_size = 0

            for raw_chunk in raw_chunks:
                if not isinstance(raw_chunk, dict):
                    raise ValueError("Each chunk must be an object")

                chunk_id = raw_chunk.get("id")
                chunk_size_value = raw_chunk.get("size")

                if not isinstance(chunk_id, str) or not _HASH_RE.fullmatch(chunk_id):
                    raise ValueError("Invalid chunk ID")

                if (
                    type(chunk_size_value) is not int
                    or not 0 < chunk_size_value <= chunk_size
                ):
                    raise ValueError("Invalid chunk size in manifest")

                total_size += chunk_size_value
                chunks.append(ChunkInfo(id=chunk_id, size=chunk_size_value))

            if total_size != size:
                raise ValueError("Chunk sizes do not match the file size")

            if size == 0 and sha256 != hashlib.sha256(b"").hexdigest():
                raise ValueError("Invalid hash for an empty file")

            files.append(
                FileInfo(
                    path=relative_path,
                    size=size,
                    sha256=sha256,
                    chunks=chunks,
                )
            )

        manifest = cls(
            format_version=version,
            chunk_size=chunk_size,
            files=files,
        )
        return manifest
