from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--gate", action="store", default="")


def gate_name(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--gate") or os.environ.get("MEI_GATE", "")


def require_path(path: Path, request: pytest.FixtureRequest, owner_gate: str) -> None:
    if path.exists():
        return
    if gate_name(request) == owner_gate:
        pytest.fail(f"missing required artifact for {owner_gate}: {path}")
    pytest.skip(f"{path.name} not produced yet")
