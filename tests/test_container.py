import zipfile

import pytest

from yt_archiver.container import create_container
from yt_archiver.packer import pack_directory


def test_create_container(tmp_path):
    source = tmp_path / "source"
    source.mkdir()

    (source / "hello.txt").write_text("hello world", encoding="utf-8")

    (source / "empty.txt").write_bytes(b"")

    packed = tmp_path / "packed"
    pack_directory(source, packed)

    output = tmp_path / "backup.yta"
    create_container(packed, output)

    assert output.is_file()

    with zipfile.ZipFile(output, "r") as container:
        names = set(container.namelist())

    assert "manifest.json" in names
    assert len([name for name in names if name.startswith("chunks/")]) == 1


def test_container_does_not_overwrite(tmp_path):
    packed = tmp_path / "packed"
    packed.mkdir()

    output = tmp_path / "backup.yta"

    output.write_bytes(b"keep me")

    with pytest.raises(FileExistsError):
        create_container(packed, output)

    assert output.read_bytes() == b"keep me"
