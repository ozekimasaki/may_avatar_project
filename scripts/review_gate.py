"""Gate review helper: schema 検証、予算、前 Gate PASS 確認。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import jsonschema
import yaml

from scripts.budget import count_budget
from scripts.repo import ROOT, sha256_file

SCHEMA = ROOT / "07_reviews" / "schema" / "gate_review.schema.json"
GATES = ROOT / "07_reviews" / "gates.yaml"
REPORTS = ROOT / "07_reviews" / "reports"


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def load_gates() -> dict:
    return yaml.safe_load(GATES.read_text(encoding="utf-8"))


def validate_schema(doc: dict) -> None:
    jsonschema.validate(instance=doc, schema=load_schema())


def latest_review(gate: str) -> Path | None:
    folder = REPORTS / gate
    if not folder.exists():
        return None
    files = sorted(folder.glob("review_*.json"))
    return files[-1] if files else None


def previous_gate_passed(gate: str) -> bool:
    order = load_gates()["order"]
    if gate not in order:
        raise SystemExit(f"unknown gate {gate}")
    index = order.index(gate)
    if index == 0:
        return True
    prev = order[index - 1]
    path = latest_review(prev)
    if path is None:
        print(f"previous gate {prev} has no review", file=sys.stderr)
        return False
    doc = json.loads(path.read_text(encoding="utf-8"))
    ok = doc.get("decision") == "PASS" and doc.get("human_approved") is True
    if not ok:
        print(f"previous gate {prev} is not human-approved PASS ({path})", file=sys.stderr)
    return ok


def artifact_entries(paths: list[str]) -> list[dict]:
    entries = []
    for rel in paths:
        path = ROOT / rel
        present = path.exists()
        digest = sha256_file(path) if present and path.is_file() else None
        entries.append({"path": rel, "sha256": digest, "present": present})
    return entries


def write_review(doc: dict) -> Path:
    validate_schema(doc)
    folder = REPORTS / doc["gate"]
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = folder / f"review_{stamp}.json"
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build_stub(gate: str, tests: list[dict], decision: str, **extra) -> dict:
    spec = load_gates()["gates"][gate]
    budget = count_budget()
    doc = {
        "gate": gate,
        "spec_files": spec["spec_files"],
        "spec_sections": [str(item) for item in spec["spec_sections"]],
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
        "reviewer": extra.get("reviewer", "agent"),
        "human_approved": False,
        "notes": extra.get("notes", ""),
    }
    if decision == "ROLLBACK" and not doc["rollback_to"]:
        doc["rollback_to"] = spec.get("rollback_to")
    return doc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-schema", action="store_true")
    parser.add_argument("--gate")
    parser.add_argument("--check-previous", action="store_true")
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    if args.validate_schema:
        schema = load_schema()
        jsonschema.Draft202012Validator.check_schema(schema)
        for path in REPORTS.glob("*/review_*.json"):
            validate_schema(json.loads(path.read_text(encoding="utf-8")))
            print(f"ok {path.relative_to(ROOT)}")
        print("schema ok")
        return 0

    if args.write:
        doc = json.loads(args.write.read_text(encoding="utf-8"))
        validate_schema(doc)
        out = write_review(doc)
        print(out)
        return 0

    if args.gate and args.check_previous:
        return 0 if previous_gate_passed(args.gate) else 1

    if args.gate:
        budget = count_budget()
        print(json.dumps({"gate": args.gate, "budget": budget}, indent=2))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
