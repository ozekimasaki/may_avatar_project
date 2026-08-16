import csv
import json
from pathlib import Path

from tests.conftest import ROOT, require_path

RAW = ROOT / "05_session" / "tracking_raw.csv"
CAL = ROOT / "05_session" / "calibration_proposal.json"
COLUMNS = [
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


def test_tracking_csv_columns_and_min_rows(request):
    require_path(RAW, request, "TRACK-OK")
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0].keys()) == COLUMNS or set(COLUMNS) <= set(rows[0].keys())
    assert len(rows) >= 50


def test_silent_mouth_percentile(request):
    require_path(CAL, request, "TRACK-OK")
    doc = json.loads(CAL.read_text(encoding="utf-8"))
    assert "mouth_open" in doc["deadzone"]


def test_blink_mapping_monotonic(request):
    require_path(CAL, request, "TRACK-OK")
    doc = json.loads(CAL.read_text(encoding="utf-8"))
    assert doc["blink"]["open_maps_to"] == 1
    assert doc["blink"]["closed_maps_to"] == 0
    assert doc["blink"]["open_median"] >= doc["blink"]["closed_median"]


def test_calibration_proposal_schema(request):
    require_path(CAL, request, "TRACK-OK")
    doc = json.loads(CAL.read_text(encoding="utf-8"))
    for key in ("gain", "range", "deadzone", "smoothing"):
        assert key in doc
