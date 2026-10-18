from yt_archiver.archive_ops import verify_archive
from yt_archiver.manifest import Manifest
from pathlib import Path
import re
import zipfile
import tempfile
import stat
import shutil

_CHUNK_ID_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def create_container(source: Path, destination: Path):
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.is_dir():
        raise NotADirectoryError(source)

    if destination == source or source in destination.parents:
        raise ValueError("dest must be out of the source hahah")

    if (
        destination.suffix.lower() != ".yta"
    ):  # lmao .yta is a weird extension could make it .bk or smt but whatever
        raise ValueError("destination must use .yta")

    if destination.exists():
        raise FileExistsError(destination)

    manifest_path = source / "manifest.json"
    manifest = verify_archive(source)

    chunk_dir = source / "chunks"

    chunk_ids = {chunk.id for entry in manifest.files for chunk in entry.chunks}

    for chunk_id in chunk_ids:
        if not _CHUNK_ID_RE.fullmatch(chunk_id):
            raise ValueError("invalid chunk id")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".tmp")

    try:
        with temp_path.open("xb") as raw_file:
            with zipfile.ZipFile(
                raw_file, mode="w", compression=zipfile.ZIP_STORED, allowZip64=True
            ) as container:
                container.write(manifest_path, "manifest.json")

                for chunk_id in chunk_ids:
                    container.write(chunk_dir / chunk_id, f"chunks/{chunk_id}")

        with zipfile.ZipFile(temp_path, "r") as container:
            bad_member = container.testzip()

            if bad_member is not None:
                raise ValueError("integrity check failed")

        temp_path.replace(destination)

    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def extract_container(source: Path, destination: Path):
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.is_file():
        raise FileNotFoundError(source)

    if source == destination or source in destination.parents:
        raise ValueError("source and dest must be diff")

    if destination.exists():
        raise FileExistsError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.tmp~", dir=destination.parent)
    )

    try:
        with zipfile.ZipFile(source, "r") as container:
            members = container.infolist()
            names = [member.filename for member in members]

            if len(names) != len(set(names)):
                raise ValueError("container contains duplicates")

            for member in members:
                name = member.filename

                if name == "manifest.json":
                    pass

                elif name.startswith("chunks/"):
                    chunk_id = name.removeprefix("chunks/")

                    if not _CHUNK_ID_RE.fullmatch(chunk_id):
                        raise ValueError("invalid chunk path")

                else:
                    raise ValueError("expected path in the container")

                # i dont understand what is going on here umm ask gpt for this one
                mode = member.external_attr >> 16

                if stat.S_ISLNK(mode):
                    raise ValueError("container cant contain symlinks")

                if member.is_dir():
                    raise ValueError("unexpected directory ")

            for member in members:
                if member.file_size < 0:
                    raise ValueError("invalid member")

                if member.filename == "manifest.json":
                    output_path = temp_dir / "manifest.json"

                else:
                    chunk_id = member.filename.removeprefix("chunks/")
                    chunk_dir = temp_dir / "chunks"
                    chunk_dir.mkdir(exist_ok=True)
                    output_path = chunk_dir / chunk_id

                with container.open(member, "r") as input_file:
                    with output_path.open("xb") as output_file:
                        shutil.copyfileobj(input_file, output_file)

        manifest = Manifest.load(temp_dir / "manifest.json")

        expected_chunks = {
            chunk.id for entry in manifest.files for chunk in entry.chunks
        }

        actual_chunks = (
            {path.name for path in (temp_dir / "chunks").iterdir()}
            if (temp_dir / "chunks").exists()
            else set()
        )

        if actual_chunks != expected_chunks:
            raise ValueError("contaier chunks dont match to manifest")

        verify_archive(temp_dir)

        temp_dir.replace(destination)

        return destination
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
