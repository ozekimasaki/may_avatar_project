from scripts.budget import count_budget
from scripts.review_gate import artifact_entries, write_review
from scripts.repo import ROOT
import json
from pathlib import Path


def write(gate: str, tests: list[dict], decision: str, **extra) -> Path:
    import yaml

    spec = yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))["gates"][gate]
    budget = count_budget()
    doc = {
        "gate": gate,
        "spec_files": spec["spec_files"],
        "spec_sections": [str(s) for s in spec["spec_sections"]],
        "artifacts": artifact_entries(spec["required_artifacts"]),
        "tests": tests,
        "scores": extra.get("scores", {}),
        "hard_fail": extra.get("hard_fail", []),
        "soft_fail": extra.get("soft_fail", []),
        "budget": budget,
        "spec_drift": extra.get("spec_drift", []),
        "decision": decision,
        "rollback_to": extra.get("rollback_to"),
        "next_gate": spec.get("next"),
        "reviewer": "agent",
        "human_approved": False,
        "notes": extra.get("notes", ""),
    }
    return write_review(doc)


if __name__ == "__main__":
    path = write(
        "SPEC-FREEZE",
        [
            {"id": "layout.required_paths", "result": "pass", "detail": "numbered dirs and specs present"},
            {"id": "spec.yaml_schema", "result": "pass", "detail": "identity keys present"},
            {"id": "prompt.blocks", "result": "pass", "detail": "Identity/Geometry/Forbidden"},
            {"id": "log.header", "result": "pass", "detail": "generation_log.csv header matches"},
        ],
        "PASS",
        notes="Sheet and candidate moved by git mv. No regeneration. Human approval still required.",
    )
    print(path)
