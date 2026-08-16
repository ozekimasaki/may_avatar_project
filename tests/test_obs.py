from pathlib import Path

from tests.conftest import ROOT, require_path

NEEDED = ["face.png", "mouth.png", "eyes.png", "flower.png", "full.png"]


def test_required_screenshots(request):
    folder = ROOT / "06_obs" / "screenshots"
    for name in NEEDED:
        require_path(folder / name, request, "OBS-OK")


def test_min_resolution(request):
    from PIL import Image

    path = ROOT / "06_obs" / "screenshots" / "full.png"
    require_path(path, request, "OBS-OK")
    image = Image.open(path)
    assert image.width >= 640 and image.height >= 360


def test_face_bbox_in_frame(request):
    qa = ROOT / "06_obs" / "screenshots" / "obs_qa.json"
    require_path(qa, request, "OBS-OK")
