##@brodskyb
##Nov 16, 2026

from pathlib import Path
from dataclasses import dataclass, field
from stat import S_ISDIR, S_ISREG


@dataclass
class ScanResult:
    total_bytes: int = 0
    errors: list[str] = field(default_factory=list)
    children: dict[str, "ScanResult"] = field(default_factory=dict)
    files: dict[str, int] = field(default_factory=dict)


def logical_file_size(path: Path) -> int:
    return path.lstat().st_size


def list_children(directory: Path) -> list[Path]:
    return list(directory.iterdir())


def is_regular_file(path: Path) -> bool:
    return S_ISREG(path.lstat().st_mode)


def direct_file_bytes(directory: Path) -> int:
    total_bytes = 0
    for child in list_children(directory):
        if same_filesystem(child, directory) and is_regular_file(child):
            total_bytes += logical_file_size(child)
    return total_bytes


def is_directory(path: Path) -> bool:
    return S_ISDIR(path.lstat().st_mode)


def same_filesystem(path: Path, root: Path) -> bool:
    return path.lstat().st_dev == root.lstat().st_dev


def recursive_file_bytes(directory: Path) -> int:
    if not is_directory(directory):
        raise NotADirectoryError(directory)
    total_bytes = direct_file_bytes(directory)
    for child in list_children(directory):
        if same_filesystem(child, directory) and is_directory(child):
            total_bytes += recursive_file_bytes(child)
    return total_bytes


def list_children_for_scan(directory: Path, result: ScanResult) -> list[Path]:
    try:
        return list_children(directory)
    except OSError as error:
        result.errors.append(str(error))
        return []


def scan_directory(directory: Path) -> ScanResult:
    if not is_directory(directory):
        raise NotADirectoryError(directory)
    result = ScanResult()
    for child in list_children_for_scan(directory, result):
        try:
            if not same_filesystem(child, directory):
                continue
            if is_regular_file(child):
                size = logical_file_size(child)
                result.files[child.name] = size
                result.total_bytes += size
            elif is_directory(child):
                nested = scan_directory(child)
                result.children[child.name] = nested
                result.total_bytes += nested.total_bytes
                result.errors.extend(nested.errors)
        except OSError as error:
            result.errors.append(str(error))
    return result