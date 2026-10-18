import cv2
from pathlib import Path
import struct
import numpy as np

MAGIC = b"YTARCH01"
HEADER_SIZE = 16
WIDTH = 256
HEIGHT = 256
CHANNELS = 3
FPS = 10

FRAME_BYTES = WIDTH * HEIGHT * CHANNELS


def encode_file(source: Path, destination: Path) -> None:

    source = Path(source)
    destination = Path(destination)

    if not source.is_file():
        raise FileNotFoundError(source)

    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must differ")

    if destination.exists():
        raise FileExistsError(destination)

    if destination.suffix.lower() != ".mkv":
        raise ValueError("Output must be in mkv")

    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_path = destination.with_name(destination.stem + ".tmp.mkv")

    size = source.stat().st_size

    writer = cv2.VideoWriter(
        str(temp_path),
        cv2.VideoWriter.fourcc(*"FFV1"),
        FPS,
        (WIDTH, HEIGHT),
        True,
    )

    if not writer.isOpened():
        raise RuntimeError("Could not initialize FFV1 writer, check opencv video codec")

    try:
        with source.open("rb") as file:
            header = MAGIC + struct.pack("<Q", size)
            first_capacity = FRAME_BYTES - HEADER_SIZE
            payload = file.read(first_capacity)

            frame_data = header + payload

            frame_data += b"\x00" * (FRAME_BYTES - len(frame_data))

            writer.write(
                np.frombuffer(
                    frame_data,
                    dtype=np.uint8,
                ).reshape(HEIGHT, WIDTH, CHANNELS)
            )

            while True:
                payload = file.read(FRAME_BYTES)
                if not payload:
                    break

                payload += b"\x00" * (FRAME_BYTES - len(payload))

                writer.write(
                    np.frombuffer(
                        payload,
                        dtype=np.uint8,
                    ).reshape(HEIGHT, WIDTH, CHANNELS)
                )
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    finally:
        writer.release()

    if not temp_path.is_file() or temp_path.stat().st_size == 0:
        temp_path.unlink(missing_ok=True)
        raise ValueError("Encoding failed")

    try:
        temp_path.replace(destination)
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise
