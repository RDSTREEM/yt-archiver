from collections.abc import Iterator
from typing import BinaryIO

# Changing the way the chunker is going to work ig
# because rn it will holed everything to memory and that is not what i want
# chunk size from config?


def chunk_stream(stream: BinaryIO, chunk_size: int) -> Iterator[bytes]:
    if chunk_size <= 0:
        raise ValueError("Chunk size can not be less than 0")

    while True:
        data = stream.read(chunk_size)

        if not data:
            break

        yield data
