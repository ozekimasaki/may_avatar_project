"""Split 3x3 Face Atlas, register to master face crop, extract mouth/eye patches."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from scripts.repo import ROOT

ATLAS = ROOT / "01_art" / "face_atlas" / "mei_face_atlas_v001.png"
CROP = ROOT / "01_art" / "face_atlas" / "mei_master_face_crop_v001.png"
OUT = ROOT / "01_art" / "face_atlas" / "extracted"
CELLS = {
    (0, 0): "mouth_a",
    (0, 1): "mouth_i",
    (0, 2): "mouth_u",
    (1, 0): "mouth_e",
    (1, 1): "mouth_o",
    (1, 2): "eye_half",
    (2, 0): "eye_close",
}


def split_grid(image: np.ndarray, rows: int = 3, cols: int = 3) -> list[tuple[str, np.ndarray]]:
    h, w = image.shape[:2]
    cell_h, cell_w = h // rows, w // cols
    cells = []
    for r in range(rows):
        for c in range(cols):
            name = CELLS.get((r, c), f"spare_{r}_{c}")
            tile = image[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
            cells.append((name, tile))
    return cells


def register(cell: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ref = cv2.resize(reference, (cell.shape[1], cell.shape[0]))
    gray_a = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        cv2.findTransformECC(
            gray_b,
            gray_a,
            warp,
            cv2.MOTION_EUCLIDEAN,
            (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4),
        )
        aligned = cv2.warpAffine(cell, warp, (cell.shape[1], cell.shape[0]), flags=cv2.INTER_LINEAR)
        return aligned
    except cv2.error:
        return cell


def difference_patch(aligned: np.ndarray, reference: np.ndarray, kind: str) -> np.ndarray:
    ref = cv2.resize(reference, (aligned.shape[1], aligned.shape[0]))
    diff = cv2.absdiff(aligned, ref)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 18, 255, cv2.THRESH_BINARY)
    h, w = mask.shape
    if kind.startswith("mouth"):
        roi = np.zeros_like(mask)
        roi[int(h * 0.55) : int(h * 0.92), int(w * 0.25) : int(w * 0.75)] = 255
        mask = cv2.bitwise_and(mask, roi)
    else:
        roi = np.zeros_like(mask)
        roi[int(h * 0.28) : int(h * 0.58), int(w * 0.12) : int(w * 0.88)] = 255
        mask = cv2.bitwise_and(mask, roi)
    mask = cv2.medianBlur(mask, 5)
    bgra = cv2.cvtColor(aligned, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = mask
    return bgra


def extract(atlas_path: Path = ATLAS, crop_path: Path = CROP, out_dir: Path = OUT) -> dict:
    atlas = cv2.imread(str(atlas_path), cv2.IMREAD_COLOR)
    crop = cv2.imread(str(crop_path), cv2.IMREAD_COLOR)
    if atlas is None:
        raise FileNotFoundError(atlas_path)
    if crop is None:
        raise FileNotFoundError(crop_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {"cells": [], "grid": 9}
    for name, tile in split_grid(atlas):
        tile_path = out_dir / f"{name}_cell.png"
        cv2.imwrite(str(tile_path), tile)
        if name.startswith("spare"):
            continue
        aligned = register(tile, crop)
        patch = difference_patch(aligned, crop, name)
        patch_path = out_dir / f"{name}.png"
        cv2.imwrite(str(patch_path), patch)
        report["cells"].append({"name": name, "path": str(patch_path.relative_to(ROOT)).replace("\\", "/")})
    (out_dir / "extract_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(extract(), indent=2))
