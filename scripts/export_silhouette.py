"""Export master silhouette PNG for mesh bootstrap."""

from pathlib import Path

import cv2

from scripts.qa_master import foreground_mask
from scripts.repo import ROOT

MASTER = ROOT / "01_art" / "master" / "mei_master_v001.png"
OUT = ROOT / "04_inochi" / "meshes" / "_silhouette.png"


def main() -> Path:
    image = cv2.imread(str(MASTER), cv2.IMREAD_UNCHANGED)
    mask = foreground_mask(image)
    bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = mask
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT), bgra)
    return OUT


if __name__ == "__main__":
    print(main())
