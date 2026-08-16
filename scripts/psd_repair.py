"""RGB from KIE, alpha from existing layer. Max 2 repair calls."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from scripts.budget import count_budget
from scripts.kie_client import create_task, download_result, get_credits, poll_task, result_urls, upload_file
from scripts.repo import ROOT, append_log

PROMPT = (ROOT / "00_reference" / "prompts" / "master_repair_v001.txt").read_text(encoding="utf-8")


def composite_rgb(model_rgb: Path, alpha_source: Path, dest: Path) -> Path:
    rgb = Image.open(model_rgb).convert("RGB")
    alpha_img = Image.open(alpha_source).convert("RGBA")
    if rgb.size != alpha_img.size:
        rgb = rgb.resize(alpha_img.size)
    out = Image.merge("RGBA", (*rgb.split(), alpha_img.split()[-1]))
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return dest


def repair_layer(source_png: Path, dest_png: Path, issue: str) -> str:
    budget = count_budget()
    if budget["psd_repair"] >= 2:
        raise SystemExit("repair call cap is 2")
    if get_credits() < 1:
        raise SystemExit("no KIE credits")
    url = upload_file(source_png)
    task_id = create_task(
        "gpt-image-2-image-to-image",
        {
            "prompt": PROMPT + f"\nOnly repair: {issue}\nDo not output alpha. RGB only.\n",
            "input_urls": [url],
            "aspect_ratio": "auto",
            "resolution": "1K",
        },
    )
    data = poll_task(task_id)
    urls = result_urls(data)
    if not urls:
        raise SystemExit("no repair url")
    rgb_path = dest_png.with_suffix(".rgb.png")
    download_result(urls[0], rgb_path)
    composite_rgb(rgb_path, source_png, dest_png)
    append_log(
        {
            "id": "PSD_REPAIR",
            "model": "gpt-image-2-image-to-image",
            "mode": "REPAIR",
            "input": str(source_png).replace("\\", "/"),
            "prompt_version": "master_repair_v001",
            "output": str(dest_png).replace("\\", "/"),
            "purpose": "psd_repair",
            "accepted": "pending",
            "reason": issue,
            "next_action": "rebuild",
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
    print(repair_layer(args.source, args.dest, args.issue))


if __name__ == "__main__":
    main()
