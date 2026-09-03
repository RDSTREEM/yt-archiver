import os
from config import CHUNK_SIZE


def chunk(file_paths: list):
    chunks = []
    for path in file_paths:
        with open(path, "rb+") as file:
            b = file.read(CHUNK_SIZE)

    print(chunks)
    return chunks
