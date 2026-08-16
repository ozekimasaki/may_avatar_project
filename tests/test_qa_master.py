import json
from pathlib import Path

from tests.conftest import ROOT, require_path


def test_master_exists_and_hash(request):
    png = ROOT / "01_art" / "master" / "mei_master_v001.png"
    sha = ROOT / "01_art" / "master" / "mei_master_v001.sha256"
    require_path(png, request, "MASTER-FREEZE")
    require_path(sha, request, "MASTER-FREEZE")
    from scripts.repo import sha256_file

    assert sha.read_text(encoding="utf-8").strip().split()[0] == sha256_file(png)


def test_master_qa_schema(request):
    path = ROOT / "01_art" / "master" / "master_qa_v001.json"
    require_path(path, request, "MASTER-FREEZE")
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert "hard_fail" in doc
    assert "scores" in doc
    assert "total" in doc
    assert "decision" in doc


def test_master_size_portrait(request):
    png = ROOT / "01_art" / "master" / "mei_master_v001.png"
    require_path(png, request, "MASTER-FREEZE")
    from PIL import Image

    image = Image.open(png)
    assert image.height / image.width >= 1.2


def test_symmetry_metric(request):
    png = ROOT / "01_art" / "master" / "mei_master_v001.png"
    require_path(png, request, "MASTER-FREEZE")
    from scripts.qa_master import evaluate

    report = evaluate(png)
    assert report["metrics"]["symmetry_iou"] >= 0.55


def test_no_fullbody_after_candidate():
    from scripts.repo import read_log

    rows = read_log()
    after = False
    extra = 0
    for row in rows:
        if row.get("id") == "CANDIDATE":
            after = True
            continue
        if after and (row.get("mode") or "").upper() in {"FULL", "FULLBODY", "T2I"}:
            extra += 1
    assert extra == 0
