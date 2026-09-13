import os


def chunk_bytes(data: list, chunk_size):
    if chunk_size <= 0:
        raise ValueError("Chunk size must be a positive value")

    for start in range(0, len(data), chunk_size):
        yield data[start : start + chunk_size]
