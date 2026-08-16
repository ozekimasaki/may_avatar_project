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


def test_psd_repair_prompts():
    head = (ROOT / "00_reference" / "prompts" / "psd_head_repair_v001.txt").read_text(encoding="utf-8")
    body = (ROOT / "00_reference" / "prompts" / "psd_body_repair_v001.txt").read_text(encoding="utf-8")
    for text in (head, body):
        assert "Repair only the masked missing or corrupted region" in text
        assert "Do not redesign" in text
        assert "Output RGB only" in text
    assert "Head" in head
    assert "Body" in body


def test_log_header():
    from scripts.budget import check_header

    check_header()
