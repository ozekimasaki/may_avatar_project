"""Colorize grayscale See-Through layers from frozen Master, then split parts.

RGB comes from the frozen master. Alpha comes from See-Through occupancy
(L < 250, plus near-white pixels that sit on the master silhouette).
Never mutate the raw PSD.
"""

from __future__ import annotations

import json

import cv2
import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

from scripts.repo import ROOT, sha256_file

RAW = ROOT / "03_psd" / "raw" / "mei_seethrough_raw_v001.psd"
MANIFEST = ROOT / "03_psd" / "audit" / "layer_manifest.json"
MASTER = ROOT / "01_art" / "master" / "mei_master_v001.png"
FINAL = ROOT / "03_psd" / "final" / "mei_rigready_v001.psd"
AUDIT = ROOT / "03_psd" / "audit" / "audit.json"
PREVIEW = ROOT / "03_psd" / "final" / "rigready_preview.png"
LAYER_DIR = ROOT / "03_psd" / "final" / "layers"
RECIPE = ROOT / "04_inochi" / "rig_recipe_v001.json"

LAYER_ORDER = [
    "Hair_Back",
    "Body_Base",
    "Dress",
    "Apron",
    "Arm_L",
    "Hand_L",
    "Arm_R",
    "Hand_R",
    "Skirt",
    "Leg_L",
    "Leg_R",
    "Shoe_L",
    "Shoe_R",
    "Face",
    "Brow_L",
    "Brow_R",
    "Eye_L",
    "Eye_R",
    "Iris_L",
    "Iris_R",
    "Eyelash_L",
    "Eyelash_R",
    "Mouth",
    "Hair_Front",
    "Hair_Side_L",
    "Hair_Side_R",
    "Ahoge",
    "Headband",
    "Flower",
    "Green_Ribbon",
    "Blue_Ribbon",
    "Bell",
]

CRITICAL = {
    "Face",
    "Eye_L",
    "Eye_R",
    "Iris_L",
    "Iris_R",
    "Mouth",
    "Hair_Front",
    "Hair_Back",
    "Body_Base",
    "Arm_L",
    "Arm_R",
    "Apron",
    "Skirt",
}


def _place(canvas: np.ndarray, tile: np.ndarray, bbox: list[int]) -> None:
    x0, y0, x1, y1 = bbox
    h, w = tile.shape[:2]
    x1 = min(x0 + w, canvas.shape[1])
    y1 = min(y0 + h, canvas.shape[0])
    src = tile[: y1 - y0, : x1 - x0]
    if src.ndim == 2:
        canvas[y0:y1, x0:x1] = np.maximum(canvas[y0:y1, x0:x1], src)
    else:
        alpha = src[:, :, 3:4].astype(np.float32) / 255.0
        canvas[y0:y1, x0:x1, :3] = (
            canvas[y0:y1, x0:x1, :3] * (1 - alpha) + src[:, :, :3] * alpha
        ).astype(np.uint8)
        canvas[y0:y1, x0:x1, 3] = np.maximum(canvas[y0:y1, x0:x1, 3], src[:, :, 3])


def _occupancy_from_l(L: np.ndarray, grow: int = 0) -> np.ndarray:
    """See-Through tiles are opaque LA; shape lives in L (empty is 254–255)."""
    dark = ((L < 250).astype(np.uint8) * 255)
    if grow <= 0:
        return dark
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow))
    grown = cv2.dilate(dark, kernel)
    near = ((L < 255) & (L >= 250)).astype(np.uint8) * 255
    return np.maximum(dark, np.minimum(grown, near))


def _full_fg_bbox(bgr: np.ndarray) -> tuple[int, int, int, int, np.ndarray]:
    white = cv2.inRange(bgr, (235, 235, 235), (255, 255, 255))
    mask = cv2.bitwise_not(white)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return 0, 0, bgr.shape[1], bgr.shape[0], mask
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    return x0, y0, x1, y1, mask


def _align_master(canvas_w: int, canvas_h: int, silhouette: np.ndarray) -> np.ndarray:
    master = cv2.imread(str(MASTER), cv2.IMREAD_UNCHANGED)
    if master is None:
        raise FileNotFoundError(MASTER)
    if master.ndim == 2:
        bgr = cv2.cvtColor(master, cv2.COLOR_GRAY2BGR)
    elif master.shape[2] == 4:
        bgr = master[:, :, :3]
    else:
        bgr = master
    mx0, my0, mx1, my1, fg = _full_fg_bbox(bgr)
    mw, mh = mx1 - mx0, my1 - my0
    ys, xs = np.where(silhouette > 8)
    sx0, sy0, sx1, sy1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    scale = (sy1 - sy0) / max(mh, 1)
    new_w = max(int(mw * scale), 1)
    new_h = max(int(mh * scale), 1)
    crop = bgr[my0:my1, mx0:mx1]
    crop_mask = fg[my0:my1, mx0:mx1]
    resized = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_AREA)
    resized_mask = cv2.resize(crop_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    out = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
    px = sx0 + (sx1 - sx0) // 2 - new_w // 2
    py = sy0
    x0, y0 = max(px, 0), max(py, 0)
    x1, y1 = min(px + new_w, canvas_w), min(py + new_h, canvas_h)
    src = resized[y0 - py : y1 - py, x0 - px : x1 - px]
    src_m = resized_mask[y0 - py : y1 - py, x0 - px : x1 - px]
    out[y0:y1, x0:x1, :3] = src
    out[y0:y1, x0:x1, 3] = src_m
    return out


def _to_pil_rgba(canvas: np.ndarray) -> Image.Image:
    """Internal canvases are OpenCV BGR; PIL/PSD need RGB."""
    rgba = np.empty_like(canvas)
    rgba[:, :, :3] = cv2.cvtColor(canvas[:, :, :3], cv2.COLOR_BGR2RGB)
    rgba[:, :, 3] = canvas[:, :, 3]
    return Image.fromarray(rgba, "RGBA")


def _crop_rgba(canvas: np.ndarray) -> tuple[Image.Image, int, int]:
    alpha = canvas[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        return _to_pil_rgba(canvas), 0, 0
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    return _to_pil_rgba(canvas[y0:y1, x0:x1]), x0, y0


def _split_lr(
    canvas: np.ndarray, mid_x: int, force_geometric: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    alpha = canvas[:, :, 3]
    left = np.zeros_like(canvas)
    right = np.zeros_like(canvas)
    num, labels, stats, _ = cv2.connectedComponentsWithStats((alpha > 8).astype(np.uint8), 8)
    if force_geometric or num <= 2:
        left_mask = np.zeros(alpha.shape, np.uint8)
        left_mask[:, :mid_x] = 1
        right_mask = (1 - left_mask).astype(np.uint8)
        for dest, m in ((left, left_mask), (right, right_mask)):
            dest[:, :, :3] = canvas[:, :, :3]
            dest[:, :, 3] = (alpha * m).astype(np.uint8)
        return left, right
    for i in range(1, num):
        if stats[i, cv2.CC_STAT_AREA] < 20:
            continue
        cx = stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH] / 2
        dest = left if cx < mid_x else right
        m = labels == i
        dest[m] = canvas[m]
    if left[:, :, 3].max() <= 8 or right[:, :, 3].max() <= 8:
        return _split_lr(canvas, mid_x, force_geometric=True)
    return left, right


def _mask_from_hsv(master: np.ndarray, layer_a: np.ndarray, lo: tuple, hi: tuple) -> np.ndarray:
    hsv = cv2.cvtColor(master[:, :, :3], cv2.COLOR_BGR2HSV)
    hit = cv2.inRange(hsv, np.array(lo), np.array(hi))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    hit = cv2.morphologyEx(hit, cv2.MORPH_CLOSE, kernel)
    out = np.zeros_like(master)
    out[:, :, :3] = master[:, :, :3]
    out[:, :, 3] = np.minimum(layer_a, hit)
    return out


def _colorize(master: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    out = np.zeros_like(master)
    out[:, :, :3] = master[:, :, :3]
    out[:, :, 3] = alpha
    return out


def _centroid(alpha: np.ndarray) -> tuple[float, float]:
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        return 0.0, 0.0
    return float(xs.mean()), float(ys.mean())


def _bbox(alpha: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        return 0, 0, 0, 0
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _split_ahoge(hair: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = (hair[:, :, 3] > 8).astype(np.uint8)
    ahoge = np.zeros_like(hair)
    rest = hair.copy()
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if num > 2:
        areas = stats[1:, cv2.CC_STAT_AREA]
        tops = stats[1:, cv2.CC_STAT_TOP]
        order = np.argsort(tops)
        top_i = 1 + int(order[0])
        if stats[top_i, cv2.CC_STAT_AREA] < areas.max() * 0.45:
            m = labels == top_i
            ahoge[m] = hair[m]
            rest[m, 3] = 0
            return ahoge, rest
    for k in range(2, 9):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        eroded = cv2.erode(mask, kernel)
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(eroded, 8)
        if n2 < 3:
            continue
        top_i = 1 + int(np.argmin(st2[1:, cv2.CC_STAT_TOP]))
        if st2[top_i, cv2.CC_STAT_AREA] >= st2[1:, cv2.CC_STAT_AREA].max() * 0.4:
            continue
        seed = (lab2 == top_i).astype(np.uint8)
        grown = cv2.dilate(seed, kernel)
        m = (grown > 0) & (mask > 0)
        ys = np.where(m)[0]
        if len(ys) == 0:
            continue
        if ys.max() > hair.shape[0] * 0.35:
            continue
        ahoge[m] = hair[m]
        rest[m, 3] = 0
        return ahoge, rest
    return ahoge, rest


def _update_recipe(parts: dict[str, np.ndarray]) -> None:
    face_a = parts.get("Face", np.zeros((1, 1, 4), np.uint8))[:, :, 3]
    neck_a = parts.get("Body_Base", np.zeros_like(face_a))[:, :, 3] if "Body_Base" in parts else face_a
    ahoge_a = parts.get("Ahoge", np.zeros_like(face_a))[:, :, 3] if "Ahoge" in parts else face_a
    flower_a = parts.get("Flower", np.zeros_like(face_a))[:, :, 3] if "Flower" in parts else face_a
    fx, fy = _centroid(face_a)
    _x0, fy0, _x1, fy1 = _bbox(face_a)
    nx, ny = _centroid(neck_a)
    if nx == 0 and ny == 0:
        nx, ny = fx, fy1
    ax, ay = _centroid(ahoge_a)
    if ax == 0 and ay == 0:
        ax, ay = fx, fy0
    rx, ry = _centroid(flower_a)
    if rx == 0 and ry == 0:
        rx, ry = fx, fy1
    head_root = [round(fx, 1), round(float(fy1), 1)]
    neck_root = [round(nx, 1), round(max(ny, fy1), 1)]
    body_root = [round(fx, 1), round(fy1 + (fy1 - fy0) * 1.4, 1)]
    face_center = [round(fx, 1), round(fy, 1)]
    ahoge = [round(ax, 1), round(ay, 1)]
    ribbon = [round(rx, 1), round(ry, 1)]
    if RECIPE.exists():
        recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    else:
        recipe = {}
    recipe.setdefault("nodes", [])
    name_to_pivot = {
        "BodyRoot": body_root,
        "NeckRoot": neck_root,
        "HeadRoot": head_root,
        "Ahoge": ahoge,
        "Ribbon": ribbon,
    }
    for node in recipe.get("nodes", []):
        if node.get("name") in name_to_pivot:
            node["pivot"] = name_to_pivot[node["name"]]
    recipe["pivots"] = {
        "HeadRoot": head_root,
        "NeckRoot": neck_root,
        "BodyRoot": body_root,
        "Ahoge": ahoge,
        "Ribbon": ribbon,
        "FaceCenter": face_center,
    }
    RECIPE.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8")


def assemble() -> dict:
    raw_hash = sha256_file(RAW)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    w, h = manifest["size"]
    by_name: dict[str, np.ndarray] = {}
    dark_union = np.zeros((h, w), np.uint8)
    for layer in manifest["layers"]:
        path = ROOT / "03_psd" / "audit" / "layers" / f"{layer['index']:03d}_{layer['name']}.png"
        tile = np.array(Image.open(path).convert("LA"))
        grow = 21 if layer["name"] == "headwear" else 0
        occ = _occupancy_from_l(tile[:, :, 0], grow=grow)
        alpha = np.zeros((h, w), np.uint8)
        _place(alpha, occ, layer["bbox"])
        by_name[layer["name"]] = alpha
        dark = np.zeros((h, w), np.uint8)
        _place(dark, _occupancy_from_l(tile[:, :, 0], grow=0), layer["bbox"])
        dark_union = np.maximum(dark_union, dark)
    master = _align_master(w, h, dark_union)
    mid_x = int(np.median(np.where(dark_union > 8)[1])) if dark_union.max() else w // 2

    parts: dict[str, np.ndarray] = {}

    def add(name: str, alpha_or_rgba: np.ndarray) -> None:
        if alpha_or_rgba.ndim == 2:
            rgba = _colorize(master, alpha_or_rgba)
        else:
            rgba = alpha_or_rgba
        if rgba[:, :, 3].max() > 8:
            parts[name] = rgba

    add("Hair_Back", by_name["back hair"])
    add("Face", by_name["face"])
    add("Mouth", by_name["mouth"])

    eye_l, eye_r = _split_lr(_colorize(master, by_name["eyewhite"]), mid_x)
    iris_l, iris_r = _split_lr(_colorize(master, by_name["irides"]), mid_x)
    brow_l, brow_r = _split_lr(_colorize(master, by_name["eyebrow"]), mid_x)
    lash_l, lash_r = _split_lr(_colorize(master, by_name["eyelash"]), mid_x)
    add("Eye_L", eye_l)
    add("Eye_R", eye_r)
    add("Iris_L", iris_l)
    add("Iris_R", iris_r)
    add("Brow_L", brow_l)
    add("Brow_R", brow_r)
    add("Eyelash_L", lash_l)
    add("Eyelash_R", lash_r)

    limb_l, limb_r = _split_lr(_colorize(master, by_name["handwear"]), mid_x)
    for side, limb in (("L", limb_l), ("R", limb_r)):
        ys, xs = np.where(limb[:, :, 3] > 8)
        if len(ys) == 0:
            continue
        split_y = int(ys.min() + (ys.max() - ys.min()) * 0.72)
        arm = limb.copy()
        hand = limb.copy()
        arm[split_y:, :, 3] = 0
        hand[:split_y, :, 3] = 0
        add(f"Arm_{side}", arm)
        add(f"Hand_{side}", hand)

    leg_l, leg_r = _split_lr(_colorize(master, by_name["legwear"]), mid_x, force_geometric=True)
    shoe_l, shoe_r = _split_lr(_colorize(master, by_name["footwear"]), mid_x, force_geometric=True)
    add("Leg_L", leg_l)
    add("Leg_R", leg_r)
    add("Shoe_L", shoe_l)
    add("Shoe_R", shoe_r)

    top_dark = by_name["topwear"]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))
    apron_gate = cv2.dilate(top_dark, kernel)
    apron = _mask_from_hsv(master, apron_gate, (0, 0, 200), (180, 40, 255))
    cloth = _colorize(master, top_dark)
    cloth[:, :, 3] = np.minimum(cloth[:, :, 3], 255 - apron[:, :, 3])
    _x0, y0, _x1, y1 = _bbox(top_dark)
    waist = int(y0 + (y1 - y0) * 0.45)
    dress = cloth.copy()
    skirt = cloth.copy()
    dress[waist:, :, 3] = 0
    skirt[:waist, :, 3] = 0
    add("Apron", apron)
    add("Dress", dress)
    add("Skirt", skirt)

    neck_a = by_name["neck"]
    ribbon_src = np.maximum(apron_gate, neck_a)
    add("Blue_Ribbon", _mask_from_hsv(master, ribbon_src, (5, 15, 160), (35, 160, 255)))
    add("Bell", _mask_from_hsv(master, ribbon_src, (85, 40, 80), (130, 255, 255)))

    head_a = by_name["headwear"]
    headband = _mask_from_hsv(master, head_a, (0, 0, 180), (180, 55, 255))
    green = _mask_from_hsv(master, head_a, (35, 40, 20), (95, 255, 200))
    flower = _colorize(master, head_a)
    flower[:, :, 3] = np.minimum(
        flower[:, :, 3],
        np.minimum(255 - headband[:, :, 3], 255 - green[:, :, 3]),
    )
    flower[:, :mid_x, 3] = 0
    add("Headband", headband)
    add("Flower", flower)
    add("Green_Ribbon", green)

    hair = _colorize(master, by_name["front hair"])
    ahoge, rest = _split_ahoge(hair)
    add("Ahoge", ahoge)
    face_box = next(layer["bbox"] for layer in manifest["layers"] if layer["name"] == "face")
    side = rest.copy()
    side[: int(face_box[3] * 0.88), :, 3] = 0
    side_l, side_r = _split_lr(side, mid_x)
    front = rest.copy()
    front[:, :, 3] = np.minimum(front[:, :, 3], (255 - np.maximum(side_l[:, :, 3], side_r[:, :, 3])))
    add("Hair_Front", front)
    add("Hair_Side_L", side_l)
    add("Hair_Side_R", side_r)

    body = np.zeros_like(master)
    for key in ("neck", "ears"):
        body[:, :, :3] = master[:, :, :3]
        body[:, :, 3] = np.maximum(body[:, :, 3], by_name[key])
    add("Body_Base", body)

    psd = PSDImage.new("RGBA", (w, h), color=0)
    written = []
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    for old in LAYER_DIR.glob("*.png"):
        old.unlink()
    for name in LAYER_ORDER:
        rgba = parts.get(name)
        if rgba is None or rgba[:, :, 3].max() <= 8:
            continue
        image, left, top = _crop_rgba(rgba)
        psd.append(PixelLayer.frompil(image, psd, name=name, top=top, left=left))
        image.save(LAYER_DIR / f"{name}.png")
        written.append(name)

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    psd.save(FINAL)
    preview = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    for name in written:
        image, left, top = _crop_rgba(parts[name])
        preview.alpha_composite(image, (left, top))
    preview.convert("RGB").save(PREVIEW)

    after_raw = sha256_file(RAW)
    if after_raw != raw_hash:
        raise RuntimeError("raw PSD mutated")

    missing_critical = sorted(CRITICAL - set(written))
    audit = {
        "layers": [
            {"name": name, "rename": name, "semantic": name.lower(), "score": 90, "issues": [], "repair": False}
            for name in written
        ],
        "critical_issues": missing_critical,
        "repair_groups": [],
        "allow_partial": bool(missing_critical),
        "colorize": "master_rgb + seethrough_L_occupancy",
        "notes": "Grayscale See-Through occupancy from L. Color from frozen master. No KIE repair.",
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    _update_recipe(parts)
    report = {
        "raw_sha256": raw_hash,
        "final": str(FINAL.relative_to(ROOT)).replace("\\", "/"),
        "layers": written,
        "missing_from_target": [name for name in LAYER_ORDER if name not in written],
        "missing_critical": missing_critical,
    }
    (ROOT / "03_psd" / "final" / "rebuild_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(assemble(), indent=2))
