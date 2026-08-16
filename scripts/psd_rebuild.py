"""Rebuild rig-ready PSD. Delegates to assemble. Never mutate raw."""

from __future__ import annotations

import json

from scripts.psd_assemble import LAYER_ORDER as TARGET_TREE
from scripts.psd_assemble import assemble


def rebuild() -> dict:
    report = assemble()
    report["target_tree"] = list(TARGET_TREE)
    return report


if __name__ == "__main__":
    print(json.dumps(rebuild(), indent=2))
