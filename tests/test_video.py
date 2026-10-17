import hashlib

import pytest

from yt_archiver.video.encoder import encode_file
from yt_archiver.video.decoder import decode_file


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"hello world",
        bytes(range(256)) * 10,
    ],
)
def test_video_roundtrip(tmp_path, payload):
    original = tmp_path / "input.bin"
    video = tmp_path / "output.mkv"
    restored = tmp_path / "restored.bin"

    original.write_bytes(payload)
    encode_file(original, video)
    decode_file(video, restored)

    assert restored.read_bytes() == payload
    assert (
        hashlib.sha256(restored.read_bytes()).digest()
        == hashlib.sha256(payload).digest()
    )
