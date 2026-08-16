import json
from pathlib import Path

from tests.conftest import ROOT, require_path

RECIPE = ROOT / "04_inochi" / "rig_recipe_v001.json"
MESH_QA = ROOT / "04_inochi" / "mesh_qa_v001.json"
STEPS = ROOT / "04_inochi" / "creator_steps_v001.md"
REQUIRED_PARAMS = {
    "EyeOpen_L",
    "EyeOpen_R",
    "MouthOpen",
    "MouthForm",
    "HeadX",
    "HeadY",
    "HeadZ",
    "EyeBallX",
    "EyeBallY",
}


def test_recipe_schema(request):
    require_path(RECIPE, request, "RIG-MVP")
    doc = json.loads(RECIPE.read_text(encoding="utf-8"))
    for key in ("nodes", "pivots", "meshes", "parameters", "bindings", "physics"):
        assert key in doc


def test_required_parameters_present(request):
    require_path(RECIPE, request, "RIG-MVP")
    doc = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert set(REQUIRED_PARAMS) <= set(doc["parameters"])
    assert doc["physics"] == {}


def test_mesh_no_outside_alpha(request):
    require_path(MESH_QA, request, "RIG-MVP")
    doc = json.loads(MESH_QA.read_text(encoding="utf-8"))
    assert doc.get("pass") is True or not doc.get("hard_fail")


def test_mesh_density_caps(request):
    require_path(MESH_QA, request, "RIG-MVP")
    doc = json.loads(MESH_QA.read_text(encoding="utf-8"))
    for mesh in doc.get("meshes", []):
        assert mesh["vertex_count"] <= mesh["cap"]


def test_pivot_head_below_face_center(request):
    require_path(RECIPE, request, "RIG-MVP")
    doc = json.loads(RECIPE.read_text(encoding="utf-8"))
    head = doc["pivots"]["HeadRoot"]
    face = doc["pivots"]["FaceCenter"]
    assert head[1] > face[1]


def test_inp_not_overwriting_without_backup():
    text = STEPS.read_text(encoding="utf-8")
    assert "backups" in text
    assert "上書きしない" in text
