from pathlib import Path
from config import CHUNK_SIZE
from manifest import Manifest, FileInfo, ChunkInfo
from chunker import chunk_stream
import hashlib


def pack_directory(source: Path, dest: Path, chunk_size: int = CHUNK_SIZE) -> Manifest:
    source = source.resolve()

    if source.is_dir():
        raise NotADirectoryError(source)

    if chunk_size <= 0:
        raise ValueError("chunk size must be postive")

    if dest == source or source in dest.parents:
        raise ValueError("Destination must be outside of the source directory")

    manifest = dest / "manifest.json"

    if manifest.exists():
        raise FileExistsError("A manifest file already exists, cant overwrite")

    # assuming we have all the paths
    paths: list[Path] = []

    chunk_dir = dest / "chunks"

    chunk_dir.mkdir(parents=True, exist_ok=True)

    files: list[FileInfo] = []

    for path in paths:
        relative_path = path.relative_to(source)
        file_hash = hashlib.sha256()
        file_size = 0
        chunks: list[ChunkInfo] = []

        with path.open("rb") as stream:
            for data in chunk_stream(stream, chunk_size):
                chunk_hash = hashlib.sha256(data).hexdigest()
                chunk_path = chunk_dir / chunk_hash

                file_hash.update(data)
                file_size += len(data)

    man = Manifest(format_version=1, chunk_size=chunk_size, files=files)

    return man
