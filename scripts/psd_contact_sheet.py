"""4-tile contact sheet per layer: name / layer / checker / context."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.repo import ROOT

LAYERS = ROOT / "03_psd" / "audit" / "layers"
OUT = ROOT / "03_psd" / "audit" / "contact_sheet.png"
TILE = 256


def checker(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (200, 200, 200, 255))
    draw = ImageDraw.Draw(img)
    step = 16
    for y in range(0, size, step):
        for x in range(0, size, step):
            if (x // step + y // step) % 2 == 0:
                draw.rectangle([x, y, x + step, y + step], fill=(240, 240, 240, 255))
    return img


def fit(image: Image.Image, size: int) -> Image.Image:
    copy = image.convert("RGBA")
    copy.thumbnail((size, size))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(copy, ((size - copy.width) // 2, (size - copy.height) // 2), copy)
    return canvas


def build(out: Path = OUT, layers: Path = LAYERS) -> Path:
    files = sorted(layers.glob("*.png"))
    if not files:
        raise FileNotFoundError(layers)
    cols = 4
    rows = len(files)
    sheet = Image.new("RGBA", (TILE * cols, TILE * rows), (18, 18, 18, 255))
    font = ImageFont.load_default()
    board = checker(TILE)
    for i, path in enumerate(files):
        layer = Image.open(path).convert("RGBA")
        name_tile = Image.new("RGBA", (TILE, TILE), (32, 32, 32, 255))
        draw = ImageDraw.Draw(name_tile)
        draw.text((12, TILE // 2 - 6), path.stem[:40], fill=(240, 240, 240, 255), font=font)
        fitted = fit(layer, TILE)
        check = board.copy()
        check.paste(fitted, (0, 0), fitted)
        context = Image.new("RGBA", (TILE, TILE), (255, 255, 255, 255))
        context.paste(fitted, (0, 0), fitted)
        for col, tile in enumerate((name_tile, fitted, check, context)):
            sheet.paste(tile.convert("RGBA"), (col * TILE, i * TILE))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(out)
    return out


if __name__ == "__main__":
    print(build())
