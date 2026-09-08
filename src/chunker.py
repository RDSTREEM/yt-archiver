import os
from config import CHUNK_SIZE


def chunk(file_paths: list):
    chunks = []
    m = {}
    for path in file_paths:
        with open(path, "rb+") as file:
            size = len(file.read())
            file.seek(0)
            while file.tell() < size:
                if chunks:
                    prev_chunk = chunks[-1]
                    rem = CHUNK_SIZE - len(prev_chunk)
                    b = file.read(rem)
                    if b:
                        prev_chunk = (prev_chunk << rem) + b
                else:
                    chunks.append(file.read)

    print(chunks)
    return chunks, m
