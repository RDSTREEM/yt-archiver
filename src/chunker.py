import os
from config import CHUNK_SIZE

def chunk(file_path, cwd):
    with open(os.path.join(cwd, file_path), "rb+") as file:
        b = file.read()

    chunks = []
    print(b)
    return chunks