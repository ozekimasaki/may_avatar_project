"""Mesh QA across 04_inochi/meshes."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.mesh_build import DENSITY_CAPS
from scripts.repo import ROOT

MESH_DIR = ROOT / "04_inochi" / "meshes"
OUT = ROOT / "04_inochi" / "mesh_qa_v001.json"


def qa() -> dict:
    reports = []
    hard = []
    for path in sorted(MESH_DIR.glob("*.json")):
        mesh = json.loads(path.read_text(encoding="utf-8"))
        name = mesh.get("name", path.stem)
        cap = mesh.get("cap") or DENSITY_CAPS.get(name, DENSITY_CAPS["default"])
        item = {
            "name": name,
            "vertex_count": mesh.get("vertex_count", len(mesh.get("vertices", []))),
            "triangles": len(mesh.get("triangles", [])),
            "outside_alpha_rejected": mesh.get("outside_alpha_rejected", 0),
            "cap": cap,
            "over_cap": False,
        }
        if item["vertex_count"] > cap:
            item["over_cap"] = True
            hard.append(f"{name}_density")
        reports.append(item)
    doc = {"meshes": reports, "hard_fail": hard, "pass": not hard}
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


if __name__ == "__main__":
    print(json.dumps(qa(), indent=2))
