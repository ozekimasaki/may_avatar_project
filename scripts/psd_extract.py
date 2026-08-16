"""Extract every PSD layer to PNG + layer_manifest.json."""

from __future__ import annotations

import json
from pathlib import Path

from psd_tools import PSDImage

from scripts.repo import ROOT, sha256_file

RAW = ROOT / "03_psd" / "raw" / "mei_seethrough_raw_v001.psd"
AUDIT = ROOT / "03_psd" / "audit"
LAYERS = AUDIT / "layers"


def _walk(layer, index: int, rows: list[dict], parent: str | None) -> int:
    name = layer.name or f"layer_{index}"
    bbox = getattr(layer, "bbox", (0, 0, 0, 0))
    visible = bool(getattr(layer, "visible", True))
    opacity = int(getattr(layer, "opacity", 255) or 0)
    blend = str(getattr(layer, "blend_mode", "") or "")
    width = int(bbox[2] - bbox[0]) if bbox else 0
    height = int(bbox[3] - bbox[1]) if bbox else 0
    kind = "group" if getattr(layer, "is_group", lambda: False)() else "layer"
    rows.append(
        {
            "index": index,
            "name": name,
            "parent": parent,
            "kind": kind,
            "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])] if bbox else [0, 0, 0, 0],
            "visible": visible,
            "opacity": opacity,
            "blend_mode": blend,
            "width": width,
            "height": height,
        }
    )
    if kind == "group":
        child_parent = name
        next_index = index + 1
        for child in layer:
            next_index = _walk(child, next_index, rows, child_parent)
        return next_index
    image = layer.composite()
    if image is not None:
        LAYERS.mkdir(parents=True, exist_ok=True)
        safe = f"{index:03d}_{name}".replace("/", "_").replace("\\", "_")
        image.save(LAYERS / f"{safe}.png")
    return index + 1


def extract(psd_path: Path = RAW) -> dict:
    psd = PSDImage.open(psd_path)
    rows: list[dict] = []
    index = 0
    for layer in psd:
        index = _walk(layer, index, rows, None)
    manifest = {
        "source": str(psd_path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_file(psd_path),
        "size": [psd.width, psd.height],
        "layers": rows,
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "layer_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps({"layers": len(extract()["layers"])}))
