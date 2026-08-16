"""Crop face from frozen master. Budget-free."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from scripts.qa_master import foreground_mask, largest_bbox
from scripts.repo import ROOT

MASTER = ROOT / "01_art" / "master" / "mei_master_v001.png"
OUT = ROOT / "01_art" / "face_atlas" / "mei_master_face_crop_v001.png"


def crop_face(source: Path = MASTER, dest: Path = OUT) -> Path:
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(source)
    mask = foreground_mask(image)
    x, y, w, h = largest_bbox(mask)
    # head is the top ~38% of the character bbox, with side padding
    head_h = int(h * 0.42)
    pad_x = int(w * 0.12)
    x0 = max(0, x - pad_x)
    x1 = min(image.shape[1], x + w + pad_x)
    y0 = max(0, y - int(h * 0.04))
    y1 = min(image.shape[0], y + head_h)
    crop = image[y0:y1, x0:x1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dest), crop)
    _ = np
    return dest


if __name__ == "__main__":
    print(crop_face())
