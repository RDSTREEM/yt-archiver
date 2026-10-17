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


def verify_archive(archive: Path) -> Manifest:
    archive = archive.resolve()

    manifest_path = archive / "manifest.json"
    manifest = Manifest.load(manifest_path)

    chunk_dir = archive / "chunks"

    for entry in manifest.files:
        file_hash = hashlib.sha256()
        restored_size = 0
        print(type(entry))

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

    return manifest


def restore_archive(
    archive: Path,
    destination: Path,
) -> Manifest:
    archive = archive.resolve()
    destination = destination.resolve()

    if destination == archive or archive in destination.parents:
        raise ValueError("Restore destination can't be inside the archive")

    if destination.exists():
        if not destination.is_dir():
            raise NotADirectoryError(destination)

        if any(destination.iterdir()):
            raise FileExistsError("Restore destination must be empty")

    else:
        destination.mkdir(parents=True)

    manifest = verify_archive(archive)

    for entry in manifest.files:
        output_path = destination.joinpath(*entry.path.split("/"))

        resolved_output = output_path.resolve()

        if resolved_output == destination or destination not in resolved_output.parents:
            raise ValueError("Unsafe restore path")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        file_hash = hashlib.sha256()

        written_size = 0

        with output_path.open("xb") as output:
            for chunk in entry.chunks:
                data = _read_verified_chunk(archive / "chunks", chunk.id, chunk.size)

                output.write(data)
                file_hash.update(data)

                written_size += len(data)

        if written_size != entry.size or file_hash.hexdigest() != entry.sha256:
            output_path.unlink(missing_ok=True)
            raise ValueError("Restored file failed verification")

    return manifest
