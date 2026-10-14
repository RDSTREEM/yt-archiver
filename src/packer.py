from pathlib import Path
from config import CHUNK_SIZE
from manifest import Manifest


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

    chunk_dir = dest / "chunks"

    chunk_dir.mkdir(parents=True, exist_ok=True)

    man = Manifest(format_version=1, chunk_size=chunk_size, files=[])

    return man
