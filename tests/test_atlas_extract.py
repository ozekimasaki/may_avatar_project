import json
from pathlib import Path

import cv2

from tests.conftest import ROOT, require_path

ATLAS = ROOT / "01_art" / "face_atlas" / "mei_face_atlas_v001.png"
EXTRACTED = ROOT / "01_art" / "face_atlas" / "extracted"


def test_atlas_one_file(request):
    require_path(ATLAS, request, "FACE-ASSET-FREEZE")
    assert ATLAS.is_file()


def test_atlas_grid_9(request):
    require_path(ATLAS, request, "FACE-ASSET-FREEZE")
    image = cv2.imread(str(ATLAS))
    assert image is not None
    h, w = image.shape[:2]
    assert h >= 3 and w >= 3


def test_cell_alignment(request):
    report = EXTRACTED / "extract_report.json"
    require_path(report, request, "FACE-ASSET-FREEZE")
    doc = json.loads(report.read_text(encoding="utf-8"))
    assert doc["grid"] == 9
    assert len(doc["cells"]) >= 7


def test_only_mouth_or_lid_diff(request):
    require_path(EXTRACTED / "mouth_a.png", request, "FACE-ASSET-FREEZE")
    patch = cv2.imread(str(EXTRACTED / "mouth_a.png"), cv2.IMREAD_UNCHANGED)
    assert patch.shape[2] == 4
    alpha = patch[:, :, 3]
    h, w = alpha.shape
    upper = alpha[: int(h * 0.4)].mean()
    lower = alpha[int(h * 0.55) :].mean()
    assert lower >= upper * 0.5 or alpha.mean() < 20


def test_extracted_assets_present(request):
    names = ["mouth_a", "mouth_i", "mouth_u", "mouth_e", "mouth_o", "eye_half", "eye_close"]
    for name in names:
        require_path(EXTRACTED / f"{name}.png", request, "FACE-ASSET-FREEZE")


def test_g002_retry_at_most_one():
    from scripts.repo import read_log

    retries = [row for row in read_log() if row.get("id") in {"G002R", "G002"}]
    g002r = [row for row in retries if row.get("id") == "G002R"]
    assert len(g002r) <= 1
