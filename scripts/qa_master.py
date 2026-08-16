from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import yaml

from scripts.repo import ROOT

CANDIDATE = ROOT / "01_art" / "candidates" / "avatar_base.png"
SPEC = ROOT / "00_reference" / "character_spec.yaml"
MASTER_DIR = ROOT / "01_art" / "master"


def _hex_to_bgr(value: str) -> np.ndarray:
    value = value.lstrip("#")
    rgb = tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    return np.array(rgb[::-1], dtype=np.float32)


def foreground_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    # near-white / near-empty background
    white = cv2.inRange(bgr, (235, 235, 235), (255, 255, 255))
    mask = cv2.bitwise_not(white)
    # drop tiny specks
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    _ = hsv
    return mask


def largest_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0, 0, mask.shape[1], mask.shape[0]
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    return x, y, w, h


def component_count(mask: np.ndarray, y0: float, y1: float) -> int:
    h, w = mask.shape
    band = mask[int(h * y0) : int(h * y1), :]
    num, _labels, stats, _ = cv2.connectedComponentsWithStats((band > 0).astype(np.uint8), 8)
    areas = stats[1:, cv2.CC_STAT_AREA] if num > 1 else np.array([])
    return int(np.sum(areas > band.size * 0.01))


def foreground_runs(mask: np.ndarray, y0: float, y1: float, min_width_ratio: float = 0.04) -> int:
    """Count separated foreground columns in a horizontal band (gaps = background)."""
    h, w = mask.shape
    band = mask[int(h * y0) : max(int(h * y1), int(h * y0) + 1), :]
    if band.size == 0:
        return 0
    col = (band > 0).mean(axis=0) > 0.18
    min_w = max(int(w * min_width_ratio), 4)
    runs = 0
    length = 0
    for flag in col.tolist():
        if flag:
            length += 1
        else:
            if length >= min_w:
                runs += 1
            length = 0
    if length >= min_w:
        runs += 1
    return runs


def hsv_region_hit(bgr: np.ndarray, mask: np.ndarray, hsv_lo: tuple, hsv_hi: tuple, min_frac: float = 0.02) -> bool:
    if mask.sum() == 0:
        return False
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    region = cv2.inRange(hsv, np.array(hsv_lo), np.array(hsv_hi))
    return float((region[mask > 0] > 0).mean()) > min_frac


def palette_hits(bgr: np.ndarray, mask: np.ndarray, spec: dict) -> float:
    pixels = bgr[mask > 0].astype(np.float32)
    if len(pixels) == 0:
        return 0.0
    keys = ["hair", "eyes", "dress", "apron", "tights", "neck_ribbon", "bell"]
    hits = 0
    for key in keys:
        target = _hex_to_bgr(spec["palette"][key])
        dist = np.linalg.norm(pixels - target, axis=1)
        if np.percentile(dist, 5) < 80:
            hits += 1
    return hits / len(keys)


def symmetry_score(mask: np.ndarray) -> float:
    h, w = mask.shape
    left = mask[:, : w // 2]
    right = cv2.flip(mask[:, w - w // 2 :], 1)
    width = min(left.shape[1], right.shape[1])
    left = left[:, :width]
    right = right[:, :width]
    union = np.logical_or(left > 0, right > 0).sum()
    if union == 0:
        return 0.0
    inter = np.logical_and(left > 0, right > 0).sum()
    return float(inter / union)


def evaluate(path: Path = CANDIDATE) -> dict:
    path = Path(path).resolve()
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    h, w = image.shape[:2]
    mask = foreground_mask(image)
    x, y, bw, bh = largest_bbox(mask)
    hard_fail: list[str] = []
    soft_fail: list[str] = []

    aspect = h / max(w, 1)
    if aspect < 1.2:
        hard_fail.append("not_portrait_front")
    if y <= 1:
        hard_fail.append("cropped_ahoge")
    if y + bh >= h - 2:
        hard_fail.append("cropped_full_body")
    if x <= 1 or x + bw >= w - 2:
        soft_fail.append("tight_horizontal_crop")

    # Character-relative bands. A dress often joins the legs into one blob;
    # a background gap between two foreground runs is the spec check.
    y_arm0, y_arm1 = (y + bh * 0.38) / h, (y + bh * 0.58) / h
    y_leg0, y_leg1 = (y + bh * 0.78) / h, (y + bh * 0.92) / h
    arms = max(component_count(mask, y_arm0, y_arm1), foreground_runs(mask, y_arm0, y_arm1))
    legs = max(component_count(mask, y_leg0, y_leg1), foreground_runs(mask, y_leg0, y_leg1, 0.03))
    if arms < 2:
        hard_fail.append("fused_arms")
    if legs < 2:
        hard_fail.append("one_leg")

    hair_mask = np.zeros_like(mask)
    hair_mask[y : y + max(bh // 5, 1), x : x + bw] = mask[y : y + max(bh // 5, 1), x : x + bw]
    body_mask = np.zeros_like(mask)
    body_mask[y + bh // 3 : y + int(bh * 0.7), x : x + bw] = mask[y + bh // 3 : y + int(bh * 0.7), x : x + bw]
    face_band = mask[y : y + max(bh // 3, 1), x : x + bw]
    face_img = image[y : y + max(bh // 3, 1), x : x + bw]
    identity_flags = {
        "hair_brown": bool(hsv_region_hit(image, hair_mask, (5, 40, 30), (25, 255, 180))),
        "eye_green": bool(hsv_region_hit(face_img, face_band, (35, 30, 40), (110, 255, 255), 0.01)),
        "apron_white": bool(hsv_region_hit(image, body_mask, (0, 0, 180), (180, 50, 255))),
        "dress_brown": bool(hsv_region_hit(image, body_mask, (5, 40, 20), (25, 255, 160))),
        "tights_green": bool(hsv_region_hit(image, mask, (35, 40, 15), (95, 255, 120))),
    }
    pal = palette_hits(image, mask, spec)
    ident = (sum(identity_flags.values()) / len(identity_flags) + pal) / 2
    if ident < 0.35:
        hard_fail.append("different_character")

    # Flower/ribbon on one side; do not demand silhouette IoU of a mirrored twin.
    body_only = mask.copy()
    body_only[: y + bh // 4] = 0
    sym = max(symmetry_score(mask), symmetry_score(body_only))
    cx = x + bw / 2
    centered = abs(cx - w / 2) / w < 0.08
    if sym < 0.50 or not centered:
        hard_fail.append("not_front_view")

    mid = face_img.shape[1] // 2
    left = face_img[:, :mid][face_band[:, :mid] > 0]
    right = face_img[:, mid:][face_band[:, mid:] > 0]
    if len(left) and len(right):
        eye_delta = float(np.linalg.norm(left.mean(axis=0) - right.mean(axis=0)))
        if eye_delta > 55:
            hard_fail.append("eyes_asymmetric")
    else:
        eye_delta = 0.0

    front = 15
    if abs(aspect - 1.5) > 0.25:
        front -= 5
        soft_fail.append("aspect_not_2_3")
    if not centered:
        front -= 5
    scores = {
        "identity": int(round(25 * min(1.0, ident + 0.15))),
        "front_view": max(front, 0),
        "symmetry": int(round(10 * min(1.0, max(0.0, (sym - 0.45) / 0.35)))),
        "arm_separation": 10 if arms >= 3 else (8 if arms == 2 else 0),
        "leg_separation": 10 if legs >= 2 else 0,
        "hair_separation": 10 if identity_flags["hair_brown"] else 6,
        "clothing_separation": 10 if identity_flags["apron_white"] and identity_flags["dress_brown"] else 6,
        "readability": 5 if min(h, w) >= 768 else 3,
        "background": 5 if (mask == 0).mean() > 0.25 else 2,
    }
    total = int(sum(scores.values()))

    if scores["arm_separation"] < 10:
        soft_fail.append("weak_arm_gap")
    if scores["leg_separation"] < 10:
        soft_fail.append("weak_leg_gap")
    if not identity_flags["eye_green"]:
        soft_fail.append("eye_green_weak")

    if hard_fail:
        decision = "STOP"
    elif total >= 90:
        decision = "FREEZE"
    elif total >= 80:
        decision = "MASK_EDIT"
    else:
        decision = "STOP"

    return {
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "width": w,
        "height": h,
        "aspect": round(aspect, 3),
        "bbox": [int(x), int(y), int(bw), int(bh)],
        "metrics": {
            "symmetry_iou": round(sym, 4),
            "palette_hit": round(pal, 4),
            "arm_components": arms,
            "leg_components": legs,
            "eye_delta": round(eye_delta, 2),
            "identity_flags": identity_flags,
            "ident": round(ident, 4),
        },
        "hard_fail": hard_fail,
        "soft_fail": soft_fail,
        "scores": scores,
        "total": total,
        "decision": decision,
    }


def main() -> None:
    report = evaluate()
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    out = MASTER_DIR / "master_qa_v001.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"total": report["total"], "decision": report["decision"], "hard_fail": report["hard_fail"]}))


if __name__ == "__main__":
    main()
