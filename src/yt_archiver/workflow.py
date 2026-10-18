import tempfile
from pathlib import Path

from yt_archiver.archive_ops import restore_archive
from yt_archiver.container import create_container, extract_container
from yt_archiver.manifest import Manifest
from yt_archiver.packer import pack_directory
from yt_archiver.video.encoder import encode_file
from yt_archiver.video.decoder import decode_file


def backup_directory(source: Path, destination: Path) -> Manifest:
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.is_dir():
        raise NotADirectoryError(source)

    if destination.suffix.lower() != ".mkv":
        raise ValueError("backup must be in mkv")

    if destination.exists():
        raise FileExistsError(destination)

    if destination == source or source in destination.parents:
        raise ValueError("vid must be outside of the source")

    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="yt-archiver-", dir=destination.parent
    ) as temp:
        workspace = Path(temp)
        packed_dir = workspace / "packed"
        container_path = workspace / "backup.yta"

        manifest = pack_directory(source, packed_dir)
        create_container(packed_dir, container_path)
        encode_file(container_path, destination)

        return manifest


def restore_video(source: Path, destination: Path):
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.is_file():
        raise FileNotFoundError(source)

    if source.suffix.lower() != ".mkv":
        raise ValueError("backup must be in mkv")

    if destination.exists():
        raise FileExistsError(destination)

    if destination == source or source in destination.parents:
        raise ValueError("vid must be outside of the source")

    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="yt-archiver-", dir=destination.parent
    ) as temp:
        workspace = Path(temp)
        container_path = workspace / "backup.yta"
        extracted_dir = workspace / "extracted"

        decode_file(source, container_path)
        extract_container(container_path, extracted_dir)
        manifest = restore_archive(extracted_dir, destination)

    return manifest
