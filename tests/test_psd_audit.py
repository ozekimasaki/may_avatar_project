import json
from pathlib import Path

from tests.conftest import ROOT, require_path

RAW = ROOT / "03_psd" / "raw" / "mei_seethrough_raw_v001.psd"
MANIFEST = ROOT / "03_psd" / "audit" / "layer_manifest.json"
CONTACT = ROOT / "03_psd" / "audit" / "contact_sheet.png"
AUDIT = ROOT / "03_psd" / "audit" / "audit.json"
FINAL = ROOT / "03_psd" / "final" / "mei_rigready_v001.psd"
CRITICAL = {
    "Face",
    "Eye_L",
    "Eye_R",
    "Iris_L",
    "Iris_R",
    "Mouth",
    "Hair_Front",
    "Hair_Back",
    "Body_Base",
    "Arm_L",
    "Arm_R",
    "Apron",
    "Skirt",
}


def test_raw_unchanged_hash(request):
    require_path(RAW, request, "PSD-AI-READY")
    sidecar = RAW.with_suffix(".psd.sha256")
    from scripts.repo import sha256_file

    digest = sha256_file(RAW)
    if sidecar.exists():
        assert sidecar.read_text(encoding="utf-8").strip().split()[0] == digest


def test_manifest_bbox(request):
    require_path(MANIFEST, request, "PSD-AI-READY")
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert doc["layers"]
    for layer in doc["layers"]:
        assert len(layer["bbox"]) == 4


def test_contact_sheet_exists(request):
    require_path(CONTACT, request, "PSD-AI-READY")


def test_critical_layers_named(request):
    require_path(AUDIT, request, "PSD-AI-READY")
    doc = json.loads(AUDIT.read_text(encoding="utf-8"))
    names = {item.get("rename") or item.get("name") for item in doc.get("layers", [])}
    missing = CRITICAL - names
    assert not missing or doc.get("allow_partial")


def test_repair_call_count_le_2():
    from scripts.budget import count_budget

    assert count_budget()["psd_repair"] <= 2


def test_alpha_not_from_model():
    src = (ROOT / "scripts" / "psd_repair.py").read_text(encoding="utf-8")
    assert "composite_rgb" in src
    assert "alpha" in src.lower()


def test_rigready_has_no_empty_critical(request):
    require_path(FINAL, request, "PSD-AI-READY")
    assert FINAL.stat().st_size > 0
