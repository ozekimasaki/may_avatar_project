import json
import os
import subprocess
import sys

from tests.conftest import ROOT


def _run_script(rel: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, str(ROOT / rel), *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_review_gate_cli_without_pythonpath():
    result = _run_script("scripts/review_gate.py", "--validate-schema")
    assert result.returncode == 0, result.stderr
    assert "schema ok" in result.stdout


def test_budget_cli_without_pythonpath():
    result = _run_script("scripts/budget.py", "--check-header")
    assert result.returncode == 0, result.stderr
    assert "header ok" in result.stdout


def test_inx_inspect_cli_without_pythonpath():
    result = _run_script("scripts/inx_inspect.py")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["magic"] == "TRNSRTS"
    assert payload["version"] == "v0.8.6"


def test_review_gate_module_invocation():
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.review_gate", "--validate-schema"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "schema ok" in result.stdout
