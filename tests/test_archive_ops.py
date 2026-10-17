import pytest

from archive_ops import restore_archive, verify_archive
from packer import pack_directory


def test_pack_verify_restore_roundtrip(tmp_path):
    source = tmp_path / "source"
    source.mkdir()

    (source / "hello.txt").write_bytes(b"Hello world")
    (source / "empty.txt").write_bytes(b"")

    nested = source / "nested"

    nested.mkdir()

    (nested / "data.bin").write_bytes(bytes(range(256)) * 20)

    archive = tmp_path / "archive"
    restored = tmp_path / "restored"

    pack_directory(source, archive, chunk_size=128)

    manifest = verify_archive(archive)
    assert len(manifest.files) == 3

    restore_archive(archive, restored)

    for original in source.rglob("*"):
        if original.is_file():
            relative = original.relative_to(source)
            output = restored / relative

            assert output.is_file()
            assert output.read_bytes() == original.read_bytes()


def test_corrputed_chunk_is_detected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "data.bin").write_bytes(b"some important test data")

    archive = tmp_path / "archive"

    pack_directory(source, archive, chunk_size=8)

    manifest = verify_archive(archive)
    chunk_id = manifest.files[0].chunks[0].id
    chunk_path = archive / "chunks" / chunk_id

    chunk_path.write_bytes(b"corrupted")

    with pytest.raises(ValueError):
        verify_archive(archive)


def test_restore_refuses_nonempty_destination(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "data.bin").write_bytes(b"haelooo")

    archive = tmp_path / "archive"

    pack_directory(source, archive, chunk_size=8)

    destination = tmp_path / "restored"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(FileExistsError):
        restore_archive(archive, destination)

    assert marker.read_text(encoding="utf-8") == "do not overwrite"
