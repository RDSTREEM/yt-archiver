from yt_archiver.workflow import backup_directory, restore_video


def test_backup_and_restore_video(tmp_path):
    source = tmp_path / "original"
    source.mkdir()

    (source / "hello.txt").write_text("hello world", encoding="utf-8")
    nested = source / "nested"
    nested.mkdir()

    (nested / "data.bin").write_bytes(bytes(range(256)) * 10)
    (source / "empty.txt").write_bytes(b"")

    video = tmp_path / "backup.mkv"

    manifest = backup_directory(source, video)

    assert video.is_file()
    assert video.stat().st_size > 0
    assert len(manifest.files) == 3

    restored = tmp_path / "restored"
    restored_manifest = restore_video(video, restored)

    assert len(restored_manifest.files) == 3
    assert (restored / "hello.txt").read_text(encoding="utf-8") == "hello world"

    assert (restored / "nested" / "data.bin").read_bytes() == bytes(range(256)) * 10

    assert (restored / "empty.txt").read_bytes() == b""
