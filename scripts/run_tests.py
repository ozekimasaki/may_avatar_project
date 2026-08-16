"""Gate 単位で pytest を回す。失敗したら次 Gate に進まない。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_gates() -> dict:
    return yaml.safe_load((ROOT / "07_reviews" / "gates.yaml").read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", required=True)
    parser.add_argument("--extra", nargs="*", default=[])
    args = parser.parse_args()
    gates = load_gates()["gates"]
    if args.gate not in gates:
        print(f"unknown gate: {args.gate}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["MEI_GATE"] = args.gate
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q", f"--gate={args.gate}", *args.extra]
    print(" ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT, env=env)


if __name__ == "__main__":
    sys.exit(main())
