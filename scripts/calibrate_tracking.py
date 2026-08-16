"""Tracking CSV → calibration proposal (gain, range, deadzone, smoothing)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from scripts.repo import ROOT

RAW = ROOT / "05_session" / "tracking_raw.csv"
OUT = ROOT / "05_session" / "calibration_proposal.json"
REQUIRED = [
    "timestamp",
    "label",
    "eye_open_l",
    "eye_open_r",
    "mouth_open",
    "head_x",
    "head_y",
    "head_z",
    "eye_ball_x",
    "eye_ball_y",
]


def load_rows(path: Path = RAW) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _col(rows: list[dict], name: str, label: str | None = None) -> np.ndarray:
    values = []
    for row in rows:
        if label and row.get("label") != label:
            continue
        values.append(float(row[name]))
    return np.array(values, dtype=float)


def calibrate(path: Path = RAW) -> dict:
    rows = load_rows(path)
    silent = _col(rows, "mouth_open", "mouth_closed")
    if silent.size == 0:
        silent = _col(rows, "mouth_open", "neutral")
    blink_open = np.concatenate(
        [_col(rows, "eye_open_l", "neutral"), _col(rows, "eye_open_r", "neutral")]
    )
    blink_closed = np.concatenate(
        [_col(rows, "eye_open_l", "blink"), _col(rows, "eye_open_r", "blink")]
    )
    mouth_p95 = float(np.percentile(silent, 95)) if silent.size else 0.0
    proposal = {
        "gain": {
            "head_x": 1.0,
            "head_y": 1.0,
            "head_z": 1.0,
            "eye_ball_x": 1.0,
            "eye_ball_y": 1.0,
            "mouth_open": 1.0,
        },
        "range": {
            "head_x": [_stat(rows, "head_x")],
            "head_y": [_stat(rows, "head_y")],
            "head_z": [_stat(rows, "head_z")],
        },
        "deadzone": {"mouth_open": mouth_p95},
        "smoothing": {"head": 0.35, "eyes": 0.2, "mouth": 0.25},
        "blink": {
            "open_median": float(np.median(blink_open)) if blink_open.size else 1.0,
            "closed_median": float(np.median(blink_closed)) if blink_closed.size else 0.0,
            "open_maps_to": 1,
            "closed_maps_to": 0,
        },
        "stats": {
            "rows": len(rows),
            "mouth_closed_p95": mouth_p95,
        },
    }
    OUT.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
    return proposal


def _stat(rows: list[dict], name: str) -> dict:
    values = _col(rows, name)
    if values.size == 0:
        return {"min": 0, "max": 0, "median": 0, "std": 0}
    return {
        "min": float(values.min()),
        "max": float(values.max()),
        "median": float(np.median(values)),
        "std": float(values.std()),
        "noise": float(np.median(np.abs(np.diff(values)))) if values.size > 1 else 0.0,
    }


if __name__ == "__main__":
    print(json.dumps(calibrate()["deadzone"]))
