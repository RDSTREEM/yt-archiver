import os
from config import CHUNK_SIZE


def chunk(file_paths: list):
    chunks: list[bytes] = []
    m = {}
    for path in file_paths:
        with open(path, "rb+") as file:
            data = file.read()
            prev_chunk = b"" if not chunks else chunks[-1]
            # i = 0
            while len(data) > 0:
                rem = CHUNK_SIZE - len(prev_chunk)
                current = data[rem:]
                if rem > 0:
                    chunks[-1] = (prev_chunk << rem) + current
                else:
                    chunk.append(current)
                data = data[rem:]

    print(chunks)
    return chunks, m
