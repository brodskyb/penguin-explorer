##@brodskyb
##Nov 16, 2026

from pathlib import Path
from stat import S_ISREG


def logical_file_size(path: Path) -> int:
    return path.lstat().st_size


def list_children(directory: Path) -> list[Path]:
    return list(directory.iterdir())


def is_regular_file(path: Path) -> bool:
    return S_ISREG(path.lstat().st_mode)


def direct_file_bytes(directory: Path) -> int:
    total_bytes = 0
    for child in list_children(directory):
        if is_regular_file(child):
            total_bytes += logical_file_size(child)
    return total_bytes