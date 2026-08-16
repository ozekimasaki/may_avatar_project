"""Verify pins.yaml and required frozen artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from scripts.repo import ROOT, sha256_file

PINS = ROOT / "08_repro" / "pins.yaml"


def check() -> int:
    pins = yaml.safe_load(PINS.read_text(encoding="utf-8"))
    errors: list[str] = []
    commit = (ROOT / pins["see_through"]["commit_file"]).read_text(encoding="utf-8").strip()
    if len(commit) < 12:
        errors.append("see-through commit pin missing")
    for rel in (
        pins["images"]["character_sheet"],
        pins["images"]["master_candidate"],
    ):
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
        else:
            sha256_file(path)
    if pins["kie"]["t2i_forbidden_for_master"] is not True:
        errors.append("t2i must stay forbidden for master")
    if pins["inochi"]["nightly_forbidden"] is not True:
        errors.append("nightly creator must stay forbidden")
    if pins["budget"]["full_body_after_master_freeze"] != 0:
        errors.append("full body after freeze must be 0")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("repro pins ok")
    return 0


if __name__ == "__main__":
    sys.exit(check())
