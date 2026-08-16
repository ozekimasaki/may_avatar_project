"""Build rig_recipe_v001.json from master bbox. Physics empty for MVP."""

from __future__ import annotations

import json

from scripts.qa_master import CANDIDATE, evaluate, foreground_mask, largest_bbox
import cv2

from scripts.repo import ROOT

OUT = ROOT / "04_inochi" / "rig_recipe_v001.json"
MASTER = ROOT / "01_art" / "master" / "mei_master_v001.png"


def build() -> dict:
    source = MASTER if MASTER.exists() else CANDIDATE
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    mask = foreground_mask(image)
    x, y, w, h = largest_bbox(mask)
    cx = x + w / 2
    face_center = [cx, y + h * 0.18]
    head_root = [cx, y + h * 0.28]
    neck_root = [cx, y + h * 0.32]
    body_root = [cx, y + h * 0.55]
    ahoge = [cx, y + h * 0.02]
    ribbon = [cx, y + h * 0.34]
    recipe = {
        "nodes": [
            {"name": "BodyRoot", "parent": None, "pivot": body_root, "children": ["NeckRoot", "Arm_L", "Arm_R", "Skirt"]},
            {"name": "NeckRoot", "parent": "BodyRoot", "pivot": neck_root, "children": ["HeadRoot"]},
            {
                "name": "HeadRoot",
                "parent": "NeckRoot",
                "pivot": head_root,
                "children": ["Face", "Eye_L", "Eye_R", "Iris_L", "Iris_R", "Mouth", "Hair_Front", "Ahoge"],
            },
            {"name": "Ahoge", "parent": "HeadRoot", "pivot": ahoge, "children": []},
            {"name": "Ribbon", "parent": "HeadRoot", "pivot": ribbon, "children": []},
        ],
        "pivots": {
            "HeadRoot": head_root,
            "NeckRoot": neck_root,
            "BodyRoot": body_root,
            "Ahoge": ahoge,
            "Ribbon": ribbon,
            "FaceCenter": face_center,
        },
        "meshes": {},
        "parameters": {
            "EyeOpen_L": {"min": 0, "max": 1, "default": 1},
            "EyeOpen_R": {"min": 0, "max": 1, "default": 1},
            "MouthOpen": {"keys": [0, 0.3, 0.6, 1.0], "default": 0},
            "MouthForm": {"keys": [-1, 0, 1], "default": 0},
            "HeadX": {"min": -1, "max": 1, "default": 0},
            "HeadY": {"min": -1, "max": 1, "default": 0},
            "HeadZ": {"min": -1, "max": 1, "default": 0},
            "EyeBallX": {"min": -1, "max": 1, "default": 0},
            "EyeBallY": {"min": -1, "max": 1, "default": 0},
        },
        "bindings": {
            "EyeOpen_L": "eye_open_master_to_atlas",
            "EyeOpen_R": "eye_open_master_to_atlas",
            "MouthOpen": "mouth_close_master_to_atlas_vowels",
        },
        "physics": {},
        "expressions": {},
        "notes": {
            "blink_open": "Master",
            "blink_half_close": "Atlas",
            "head_order": ["HeadZ", "HeadX", "HeadY"],
            "headroot_is_neck_join": True,
        },
    }
    _ = evaluate
    OUT.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8")
    return recipe


if __name__ == "__main__":
    print(json.dumps({"pivots": list(build()["pivots"])}))
