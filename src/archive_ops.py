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
