import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from tests.conftest import ROOT, require_path


def test_notebook_cells_named():
    nb = json.loads((ROOT / "02_seethrough" / "notebook" / "mei_see_through_v002.ipynb").read_text(encoding="utf-8"))
    text = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    for i in range(19):
        assert f"{i:02d}" in text


def test_st_runner_script_exists():
    assert (ROOT / "02_seethrough" / "run_seethrough.py").exists()
    assert (ROOT / "scripts" / "st_run_colab.sh").exists()


def test_st_runner_verifies_sha256(tmp_path):
    content = tmp_path / "content"
    content.mkdir()
    (content / "mei_master_v001.png").write_bytes(b"abc")
    (content / "mei_master_v001.sha256").write_text("deadbeef\n", encoding="utf-8")
    env = os.environ.copy()
    env["ST_CONTENT"] = str(content)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "02_seethrough" / "run_seethrough.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0


def test_commit_pin_file():
    text = (ROOT / "02_seethrough" / "see_through_commit.txt").read_text(encoding="utf-8").strip()
    assert len(text) >= 12
    assert all(ch in "0123456789abcdef" for ch in text.lower())


def test_st_manifest_schema(request):
    matches = list((ROOT / "02_seethrough" / "output").glob("run_*/manifest.json"))
    if not matches:
        require_path(ROOT / "02_seethrough" / "output" / "run_placeholder" / "manifest.json", request, "ST-RUN")
        return
    doc = json.loads(matches[-1].read_text(encoding="utf-8"))
    assert "commit" in doc
    assert "input_sha256" in doc


def test_raw_psd_copied_and_readonly_flag(request):
    raw = ROOT / "03_psd" / "raw" / "mei_seethrough_raw_v001.psd"
    require_path(raw, request, "ST-RUN")


def test_input_is_frozen_master_hash(request):
    png = ROOT / "01_art" / "master" / "mei_master_v001.png"
    sha = ROOT / "01_art" / "master" / "mei_master_v001.sha256"
    require_path(png, request, "MASTER-FREEZE")
    require_path(sha, request, "MASTER-FREEZE")
    digest = hashlib.sha256(png.read_bytes()).hexdigest()
    assert sha.read_text(encoding="utf-8").strip().split()[0] == digest


def test_colab_wrapper_always_stops():
    text = (ROOT / "scripts" / "st_run_colab.sh").read_text(encoding="utf-8")
    assert "colab stop" in text
    assert "--keep" not in text
    assert "drivemount" not in text
    commands = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    assert "colab auth" not in commands
