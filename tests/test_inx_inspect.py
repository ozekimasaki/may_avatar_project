from scripts.inx_inspect import inspect_inx
from tests.conftest import ROOT, require_path

INX = ROOT / "04_inochi" / "working" / "may.inx"


def test_inx_is_creator_v086(request):
    require_path(INX, request, "RIG-MVP")
    report = inspect_inx(INX)
    assert report["magic"] == "TRNSRTS"
    assert report["version"] == "v0.8.6"
    assert report["has_tex_section"] is True
    assert "Face" in report["part_names"]
    assert "Mouth" in report["part_names"]
    assert "Eye_L" in report["part_names"]
    assert "Hair_Front" in report["part_names"]
    assert report["node_count"] >= 20
