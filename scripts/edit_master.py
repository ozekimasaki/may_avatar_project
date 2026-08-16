"""GPT overlay local edit of the master candidate. Max 2 calls."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.kie_client import create_task, download_result, get_credits, poll_task, result_urls, upload_file
from scripts.repo import ROOT, append_log
from scripts.budget import count_budget

REPAIR_PROMPT = (ROOT / "00_reference" / "prompts" / "master_repair_v001.txt").read_text(encoding="utf-8")


def edit_master(source: Path, dest: Path, issue: str) -> str:
    budget = count_budget()
    if budget["full_gen"] + budget["local_edit"] + budget["psd_repair"] >= budget["cap"]:
        raise SystemExit("budget cap reached")
    credits = get_credits()
    if credits < 1:
        raise SystemExit("no KIE credits")
    url = upload_file(source)
    prompt = REPAIR_PROMPT + f"\nOnly repair: {issue}\n"
    task_id = create_task(
        "gpt-image-2-image-to-image",
        {
            "prompt": prompt,
            "input_urls": [url],
            "aspect_ratio": "2:3",
            "resolution": "1K",
        },
    )
    data = poll_task(task_id)
    urls = result_urls(data)
    if not urls:
        raise SystemExit(f"no result url for {task_id}")
    download_result(urls[0], dest)
    append_log(
        {
            "id": "MASTER_EDIT",
            "model": "gpt-image-2-image-to-image",
            "mode": "EDIT",
            "input": str(source).replace("\\", "/"),
            "prompt_version": "master_repair_v001",
            "output": str(dest).replace("\\", "/"),
            "purpose": "master_local_edit",
            "accepted": "pending",
            "reason": issue,
            "next_action": "qa",
            "task_id": task_id,
            "source_task_id": "",
        }
    )
    return task_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--issue", required=True)
    args = parser.parse_args()
    print(edit_master(args.source, args.dest, args.issue))


if __name__ == "__main__":
    main()
