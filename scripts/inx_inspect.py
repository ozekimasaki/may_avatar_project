"""Read-only inspector for Inochi Creator INX / INP JSON payload.

Does not write or patch the file. Stage B learns structure from a Creator-saved sample.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.repo import ROOT

MAGIC = b"TRNSRTS"
DEFAULT_INX = ROOT / "04_inochi" / "working" / "may.inx"


def _read_json_object(data: bytes, start: int) -> tuple[dict, int]:
    depth = 0
    in_str = False
    esc = False
    for index, byte in enumerate(data[start:], start):
        char = chr(byte)
        if in_str:
            if esc:
                esc = False
            elif char == "\\":
                esc = True
            elif char == '"':
                in_str = False
            continue
        if char == '"':
            in_str = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                return json.loads(data[start:end].decode("utf-8")), end
    raise ValueError("unterminated JSON payload")


def iter_nodes(node: dict):
    yield node
    for child in node.get("children") or []:
        yield from iter_nodes(child)


def param_names(payload: dict) -> list[str]:
    raw = payload.get("param") or payload.get("parameters") or []
    if raw is None:
        return []
    names: list[str] = []
    if isinstance(raw, dict):
        raw = [raw]
    for item in raw:
        if isinstance(item, dict):
            name = item.get("name")
            if name:
                names.append(str(name))
        elif isinstance(item, str):
            names.append(item)
    return names


def inspect_inx(path: Path) -> dict:
    path = path.resolve()
    data = path.read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError(f"not an Inochi container: {path}")
    start = data.find(b"{")
    if start < 0:
        raise ValueError(f"no JSON payload in {path}")
    payload, end = _read_json_object(data, start)
    nodes = list(iter_nodes(payload["nodes"])) if payload.get("nodes") else []
    names = [str(node.get("name") or "") for node in nodes]
    params = param_names(payload)
    meta = payload.get("meta") or {}
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "magic": MAGIC.decode("ascii"),
        "version": meta.get("version"),
        "node_count": len(nodes),
        "nodes": names,
        "part_names": [str(node.get("name")) for node in nodes if node.get("type") == "Part"],
        "param_count": len(params),
        "param_names": params,
        "has_tex_section": data.find(b"TEX_SECT", end) >= 0,
        "root_child_names": [
            str(child.get("name")) for child in (payload.get("nodes") or {}).get("children") or []
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_INX)
    args = parser.parse_args()
    print(json.dumps(inspect_inx(args.path), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
