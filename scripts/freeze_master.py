"""Copy candidate → frozen master. Does not generate images."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from scripts.qa_master import CANDIDATE, MASTER_DIR, evaluate
from scripts.repo import write_sha256

MASTER_PNG = MASTER_DIR / "mei_master_v001.png"
QA_JSON = MASTER_DIR / "master_qa_v001.json"


def freeze(source: Path = CANDIDATE, force: bool = False) -> dict:
    report = evaluate(source)
    QA_JSON.parent.mkdir(parents=True, exist_ok=True)
    QA_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if report["decision"] != "FREEZE" and not force:
        raise SystemExit(f"QA decision is {report['decision']} (total={report['total']}); not freezing")
    shutil.copy2(source, MASTER_PNG)
    write_sha256(MASTER_PNG)
    report["frozen"] = str(MASTER_PNG.relative_to(MASTER_PNG.parents[2])).replace("\\", "/")
    QA_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=CANDIDATE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    report = freeze(args.source, force=args.force)
    print(json.dumps({"decision": report["decision"], "total": report["total"]}))


if __name__ == "__main__":
    main()
