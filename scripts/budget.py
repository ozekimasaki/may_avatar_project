"""generation_log.csv から FULL / EDIT / REPAIR を集計する。"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_CSV = ROOT / "01_art" / "generation_log.csv"
HEADER = [
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

MODE_FULL = {"FULL", "FULLBODY", "T2I"}
MODE_EDIT = {"EDIT", "LOCAL_EDIT", "GPT_EDIT", "GROK_EDIT", "ATLAS"}
MODE_REPAIR = {"REPAIR", "PSD_REPAIR"}


def check_header(path: Path = LOG_CSV) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
    if header != HEADER:
        raise SystemExit(f"generation_log.csv header mismatch: {header}")
    return header


def count_budget(path: Path = LOG_CSV) -> dict[str, int]:
    full_gen = local_edit = psd_repair = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            mode = (row.get("mode") or "").upper()
            if mode in MODE_FULL:
                full_gen += 1
            elif mode in MODE_EDIT:
                local_edit += 1
            elif mode in MODE_REPAIR:
                psd_repair += 1
    return {
        "full_gen": full_gen,
        "local_edit": local_edit,
        "psd_repair": psd_repair,
        "cap": 6,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-header", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    check_header()
    budget = count_budget()
    if args.check_header and not args.json:
        print("header ok")
        return 0
    if args.json:
        import json

        print(json.dumps(budget))
    else:
        print(budget)
    return 0


if __name__ == "__main__":
    sys.exit(main())
