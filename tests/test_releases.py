import json
from pathlib import Path

from tests.conftest import ROOT, require_path


def test_recording_duration_ge_30min(request):
    recordings = list((ROOT / "06_obs" / "recordings").glob("*.mp4")) + list(
        (ROOT / "06_obs" / "recordings").glob("*.mkv")
    )
    if not recordings:
        require_path(ROOT / "06_obs" / "recordings" / "stream_30min.mp4", request, "RELEASE-v0.1")
        return
    path = recordings[0]
    import cv2

    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    assert frames / fps >= 30 * 60


def test_segment_contact_sheets(request):
    path = ROOT / "07_reviews" / "reports" / "RELEASE-v0.1" / "segment_contact_sheet.png"
    require_path(path, request, "RELEASE-v0.1")


def test_stream_review_schema(request):
    path = ROOT / "07_reviews" / "reports" / "RELEASE-v0.1" / "stream_review.json"
    require_path(path, request, "RELEASE-v0.1")
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key in ("blink", "mouth", "head", "eyes", "stability", "issues"):
        assert key in doc


def test_v01_budget_under_cap():
    from scripts.budget import count_budget

    budget = count_budget()
    assert budget["full_gen"] + budget["local_edit"] + budget["psd_repair"] <= budget["cap"]


def test_v02_no_new_fullbody_images():
    from scripts.repo import read_log

    extra = [
        row
        for row in read_log()
        if (row.get("mode") or "").upper() in {"FULL", "FULLBODY", "T2I"} and row.get("id") != "CANDIDATE"
    ]
    assert extra == []


def test_v02_physics_keys_present(request):
    path = ROOT / "04_inochi" / "recipe" / "physics_v002.json"
    require_path(path, request, "RELEASE-v0.2")
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key in ("BodyX", "Breath", "Ahoge", "Hair", "Ribbon"):
        assert key in doc


def test_v02_smoke_10min_schema(request):
    path = ROOT / "07_reviews" / "reports" / "RELEASE-v0.2" / "smoke_review.json"
    require_path(path, request, "RELEASE-v0.2")


def test_v03_expression_params_combo(request):
    recipe = ROOT / "04_inochi" / "rig_recipe_v001.json"
    require_path(recipe, request, "RELEASE-v0.3")


def test_v03_expression_atlas_at_most_one():
    from scripts.repo import read_log

    rows = [row for row in read_log() if "expression" in (row.get("purpose") or "").lower()]
    assert len(rows) <= 1


def test_v10_pins_present():
    assert (ROOT / "08_repro" / "pins.yaml").exists()


def test_v10_repro_check():
    from scripts.repro_check import check

    assert check() == 0
