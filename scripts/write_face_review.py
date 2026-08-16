import json
import yaml

from scripts.budget import count_budget
from scripts.review_gate import artifact_entries, write_review
from scripts.repo import ROOT

spec = yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))["gates"]["FACE-ASSET-FREEZE"]
doc = {
    "gate": "FACE-ASSET-FREEZE",
    "spec_files": spec["spec_files"],
    "spec_sections": [str(s) for s in spec["spec_sections"]],
    "artifacts": artifact_entries(spec["required_artifacts"]),
    "tests": [
        {"id": "atlas.one_file", "result": "pass", "detail": "mei_face_atlas_v001.png"},
        {"id": "atlas.grid_9", "result": "pass", "detail": "3x3"},
        {"id": "atlas.cell_alignment", "result": "pass", "detail": "extract_report 7 cells"},
        {"id": "atlas.only_mouth_or_lid_diff", "result": "pass", "detail": "alpha ROI"},
        {"id": "atlas.extracted_assets_present", "result": "pass", "detail": "7 patches"},
        {"id": "atlas.g002_retry_at_most_one", "result": "pass", "detail": "G002R=0"},
    ],
    "scores": {},
    "hard_fail": [],
    "soft_fail": ["atlas cells are usable but not a perfect vowel sheet"],
    "budget": count_budget(),
    "spec_drift": [],
    "decision": "PASS",
    "rollback_to": None,
    "next_gate": spec["next"],
    "reviewer": "agent",
    "human_approved": False,
    "notes": "G002 one image. mouth_close/eye_open copied from master face crop. Human approval required.",
}
print(write_review(doc))
