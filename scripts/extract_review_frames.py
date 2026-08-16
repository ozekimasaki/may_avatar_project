"""Extract 1 frame / 2s contact sheets from a recording. Does not send all frames to an LLM."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
from PIL import Image

from scripts.repo import ROOT

OUT_DIR = ROOT / "07_reviews" / "reports" / "RELEASE-v0.1"
SEGMENTS = [
    ("00-05", "normal"),
    ("05-10", "talk"),
    ("10-15", "blink"),
    ("15-20", "look"),
    ("20-25", "mouth"),
    ("25-30", "stress"),
]


def extract(video: Path, dest: Path = OUT_DIR, interval_s: float = 2.0) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(int(fps * interval_s), 1)
    frames: list[Image.Image] = []
    index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if index % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(rgb).resize((160, 90)))
        index += 1
    cap.release()
    if not frames:
        raise SystemExit("no frames")
    cols = 10
    rows = max(1, (len(frames) + cols - 1) // cols)
    sheet = Image.new("RGB", (160 * cols, 90 * rows), (0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, ((i % cols) * 160, (i // cols) * 90))
    path = dest / "segment_contact_sheet.png"
    sheet.save(path)
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    args = parser.parse_args()
    print(extract(args.video))


if __name__ == "__main__":
    main()
