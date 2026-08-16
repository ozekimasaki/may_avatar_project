from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_spec_yaml_schema():
    spec = yaml.safe_load((ROOT / "00_reference" / "character_spec.yaml").read_text(encoding="utf-8"))
    identity = spec["identity"]
    for key in ("hair", "eyes", "flower", "ribbon", "clothing", "shoes"):
        assert key in identity
    assert "palette" in spec
    assert spec["hard_fail"]
    assert spec["soft_fail"]


def test_prompt_blocks():
    text = (ROOT / "00_reference" / "prompts" / "master_v001.txt").read_text(encoding="utf-8")
    for needle in ("Identity", "Geometry", "Forbidden"):
        assert needle in text


def test_log_header():
    from scripts.budget import check_header

    check_header()
