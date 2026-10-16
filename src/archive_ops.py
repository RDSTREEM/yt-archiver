import hashlib
from pathlib import Path

from manifest import Manifest


def _read_verified_chunk(chunk_dir: Path, chunk_id: str, expected_size: int) -> bytes:
    chunk_path = chunk_dir / chunk_id

    if not chunk_path.is_file() or chunk_path.is_symlink():
        raise ValueError("Missing or invalid chunk")

    data = chunk_path.read_bytes()

    if len(data) != expected_size:
        raise ValueError("Incorrect size for chunk")

    if hashlib.sha256(data).hexdigest() != chunk_id:
        raise ValueError("Corrupted chunk")

    return data


def verify_archive(archive: Path):
    archive = archive.resolve()

    manifest_path = archive / "manifest.json"
    manifest = Manifest.load(manifest_path)

    chunk_dir = archive / "chunks"

    for entry in manifest.files:
        file_hash = hashlib.sha256()
        restored_size = 0

        for chunk in entry.chunks:
            data = _read_verified_chunk(
                chunk_dir,
                chunk.id,
                chunk.size,
            )

            file_hash.update(data)
            restored_size += len(data)

        if restored_size != entry.size:
            raise ValueError("Incorrect reconstructed size")

        if file_hash.hexdigest() != entry.sha256:
            raise ValueError("File checksum mismatch")
