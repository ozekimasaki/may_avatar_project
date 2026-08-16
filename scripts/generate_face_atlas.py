"""Generate Face Atlas via KIE gpt-image-2-image-to-image. One image."""

from __future__ import annotations

from pathlib import Path

from scripts.budget import count_budget
from scripts.crop_face import crop_face
from scripts.kie_client import create_task, download_result, get_credits, poll_task, result_urls, upload_file
from scripts.repo import ROOT, append_log

ATLAS = ROOT / "01_art" / "face_atlas" / "mei_face_atlas_v001.png"
PROMPT = (ROOT / "00_reference" / "prompts" / "face_atlas_v001.txt").read_text(encoding="utf-8")


def generate_atlas() -> Path:
    budget = count_budget()
    used = budget["full_gen"] + budget["local_edit"] + budget["psd_repair"]
    if used >= budget["cap"]:
        raise SystemExit("budget cap reached")
    if get_credits() < 1:
        raise SystemExit("no KIE credits")
    crop = crop_face()
    sheet = ROOT / "00_reference" / "character_sheet.png"
    urls = [upload_file(crop), upload_file(sheet)]
    task_id = create_task(
        "gpt-image-2-image-to-image",
        {
            "prompt": PROMPT,
            "input_urls": urls,
            "aspect_ratio": "1:1",
            "resolution": "1K",
        },
    )
    data = poll_task(task_id)
    result = result_urls(data)
    if not result:
        raise SystemExit(f"no atlas url for {task_id}")
    download_result(result[0], ATLAS)
    append_log(
        {
            "id": "G002",
            "model": "gpt-image-2-image-to-image",
            "mode": "ATLAS",
            "input": str(crop).replace("\\", "/"),
            "prompt_version": "face_atlas_v001",
            "output": str(ATLAS).replace("\\", "/"),
            "purpose": "face_atlas",
            "accepted": "pending",
            "reason": "g002",
            "next_action": "extract",
            "task_id": task_id,
            "source_task_id": "",
        }
    )
    return ATLAS


if __name__ == "__main__":
    print(generate_atlas())
