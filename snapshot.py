import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from scanner import scan_directory


def create_snapshot(root: Path) -> dict:
    result = scan_directory(root)
    return {
        "root": str(root.absolute()),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "tree": asdict(result),
    }


def save_snapshot(snapshot: dict, destination: Path) -> None:
    with TemporaryDirectory(dir=destination.parent) as temp_dir:
        pending = Path(temp_dir) / "snapshot.json"
        with pending.open("w", encoding="utf-8") as output:
            json.dump(snapshot, output)
        pending.replace(destination)


def load_snapshot(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)