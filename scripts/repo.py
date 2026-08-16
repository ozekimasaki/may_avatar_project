from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_CSV = ROOT / "01_art" / "generation_log.csv"
LOG_HEADER = [
    "id",
    "timestamp",
    "model",
    "mode",
    "input",
    "prompt_version",
    "output",
    "purpose",
    "accepted",
    "reason",
    "next_action",
    "task_id",
    "source_task_id",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_sha256(path: Path) -> Path:
    sidecar = path.with_name(path.stem + ".sha256")
    sidecar.write_text(sha256_file(path) + "\n", encoding="utf-8")
    return sidecar


def read_sha256_sidecar(path: Path) -> str:
    sidecar = path.with_name(path.stem + ".sha256")
    return sidecar.read_text(encoding="utf-8").strip().split()[0]


def append_log(row: dict[str, str]) -> None:
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    exists = LOG_CSV.exists()
    with LOG_CSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_HEADER)
        if not exists:
            writer.writeheader()
        payload = {key: row.get(key, "") for key in LOG_HEADER}
        if not payload["timestamp"]:
            payload["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        writer.writerow(payload)


def read_log() -> list[dict[str, str]]:
    if not LOG_CSV.exists():
        return []
    with LOG_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
