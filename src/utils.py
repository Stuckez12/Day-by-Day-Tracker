import hashlib
import logging
import shutil
from pathlib import Path


# ------------------------- CHECKSUMS ------------------------- #


def sha256_file(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# -------------------------- FOLDERS -------------------------- #


def delete_folder(path: Path):
    shutil.rmtree(path)

    if path.exists():
        error = f"Path '{path}' was not deleted"

        logging.error(error)

        raise FileExistsError(error)
