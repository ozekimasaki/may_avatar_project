"""Contour → simplify → Delaunay mesh JSON from an alpha PNG."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import Delaunay

from scripts.repo import ROOT

MESH_DIR = ROOT / "04_inochi" / "meshes"
DENSITY_CAPS = {
    "Face": 180,
    "Mouth": 220,
    "Eye_L": 120,
    "Eye_R": 120,
    "Hair_Front": 140,
    "Body_Base": 90,
    "Apron": 90,
    "default": 80,
}


def build_mesh(alpha_png: Path, name: str) -> dict:
    image = cv2.imread(str(alpha_png), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(alpha_png)
    if image.shape[2] == 4:
        alpha = image[:, :, 3]
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours((alpha > 8).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError(f"no contour in {alpha_png}")
    contour = max(contours, key=cv2.contourArea)
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
    cap = DENSITY_CAPS.get(name, DENSITY_CAPS["default"])
    if len(approx) > cap:
        step = int(np.ceil(len(approx) / cap))
        approx = approx[::step]
    ys, xs = np.where(alpha > 8)
    if len(xs) > 40:
        idx = np.linspace(0, len(xs) - 1, min(40, len(xs))).astype(int)
        interior = np.stack([xs[idx], ys[idx]], axis=1)
        points = np.unique(np.vstack([approx, interior]), axis=0)
    else:
        points = approx
    tri = Delaunay(points)
    h, w = alpha.shape
    outside = 0
    kept = []
    for simplex in tri.simplices:
        pts = points[simplex]
        centroid = pts.mean(axis=0)
        x, y = int(centroid[0]), int(centroid[1])
        if 0 <= x < w and 0 <= y < h and alpha[y, x] > 8:
            kept.append(simplex.tolist())
        else:
            outside += 1
    mesh = {
        "name": name,
        "vertices": points.tolist(),
        "triangles": kept,
        "outside_alpha_rejected": outside,
        "vertex_count": len(points),
        "cap": cap,
    }
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    (MESH_DIR / f"{name}.json").write_text(json.dumps(mesh), encoding="utf-8")
    return mesh


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    print(json.dumps({"vertices": build_mesh(args.png, args.name)["vertex_count"]}))
