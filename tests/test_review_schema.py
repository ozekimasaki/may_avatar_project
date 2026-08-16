import json
from pathlib import Path

import jsonschema
import yaml

from scripts.review_gate import SCHEMA, load_gates, load_schema, validate_schema
from tests.conftest import ROOT


def test_schema_file_exists():
    assert SCHEMA.exists()


def test_gates_yaml_order():
    doc = load_gates()
    assert doc["order"][0] == "SPEC-FREEZE"
    assert "MASTER-FREEZE" in doc["gates"]


def test_review_reports_validate():
    schema = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    reports = list((ROOT / "07_reviews" / "reports").glob("*/review_*.json"))
    for path in reports:
        validate_schema(json.loads(path.read_text(encoding="utf-8")))


def test_gate_test_ids_unique():
    gates = yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))
    seen = []
    for spec in gates["gates"].values():
        seen.extend(spec["tests"])
    assert len(seen) == len(set(seen))
