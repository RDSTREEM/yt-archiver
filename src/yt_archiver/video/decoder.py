from yt_archiver.video.encoder import (
    CHANNELS,
    FRAME_BYTES,
    HEADER_SIZE,
    MAGIC,
)

import cv2
import struct
from pathlib import Path
import numpy as np


def decode_file(source: Path, destination: Path) -> None:
    source = Path(source)
    destination = Path(destination)

    if not source.is_file():
        raise FileNotFoundError(source)

    if destination.exists():
        raise FileNotFoundError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(source))

    temp_path = destination.with_name(destination.name + ".tmp")

    if not capture.isOpened():
        raise RuntimeError("Couldn open da video")

    written = 0
    expected_size: None | int = None

    try:
        with temp_path.open("xb") as output:
            first = True

            while True:
                ok, frame = capture.read()

                if not ok:
                    break

                if frame.shape[2] != CHANNELS:
                    raise ValueError("Unexpected frame format")

                raw = np.ascontiguousarray(frame).tobytes()

                if len(raw) != FRAME_BYTES:
                    raise ValueError("Unexpected frame dimensions")

                if first:
                    if raw[:8] != MAGIC:
                        raise ValueError("Invalid video signature")

                    expected_size = struct.unpack("<Q", raw[8:HEADER_SIZE])[0]

                    if expected_size > 2**63 - 1:
                        raise ValueError("Invalid payload size")

                    payload = raw[HEADER_SIZE:]

                    first = False
                else:
                    payload = raw

                if expected_size is None:
                    raise ValueError("Header not read properly")

                remaining = expected_size - written

                if remaining < 0:
                    raise ValueError("video contains excess data")

                payload = payload[:remaining]
                output.write(payload)
                written += len(payload)

                if written == expected_size:
                    break

            if first:
                raise ValueError("Video contains no frames")

            if written != expected_size:
                raise ValueError(
                    f"Truncated video: expected {expected_size}"
                    f"bytes, recovered {written}"
                )

    except Exception as e:
        temp_path.unlink(missing_ok=True)

    finally:
        capture.release()

    try:
        temp_path.replace(destination)
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise
