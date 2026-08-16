#!/usr/bin/env python3
"""See-Through runner for Colab exec. Fail closed. Never silently downgrade torch."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CONTENT = Path(os.environ.get("ST_CONTENT", "/content"))
COMMIT_FILE = CONTENT / "see_through_commit.txt"
MASTER = CONTENT / "mei_master_v001.png"
MASTER_SHA = CONTENT / "mei_master_v001.sha256"
OUT = CONTENT / "output"
REPO = CONTENT / "see-through"
REPO_URL = "https://github.com/shitagaki-lab/see-through.git"


def die(code: int, message: str) -> None:
    print(message, file=sys.stderr, flush=True)
    raise RuntimeError(f"ST_FAIL_{code}: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_sha() -> str:
    if not MASTER.exists() or not MASTER_SHA.exists():
        die(2, "master or sha256 sidecar missing")
    expected = MASTER_SHA.read_text(encoding="utf-8").strip().split()[0]
    actual = sha256(MASTER)
    if actual != expected:
        die(3, f"SHA256 mismatch expected={expected} actual={actual}")
    return actual


def require_env() -> dict:
    import platform

    py = sys.version_info
    if py[:2] != (3, 12):
        die(4, f"Python 3.12 required, got {platform.python_version()}")
    try:
        import torch
    except ImportError:
        die(4, "torch missing")
    version = torch.__version__
    if not version.startswith("2.8.0"):
        die(4, f"PyTorch 2.8.0+cu128 required, got {version}")
    if not torch.cuda.is_available():
        die(4, "CUDA not available")
    return {
        "python": platform.python_version(),
        "torch": version,
        "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
    }


def require_python() -> None:
    import platform

    if sys.version_info[:2] != (3, 12):
        die(4, f"Python 3.12 required, got {platform.python_version()}")


def pin_clone() -> str:
    commit = COMMIT_FILE.read_text(encoding="utf-8").strip().split()[0]
    if not REPO.exists():
        subprocess.check_call(["git", "clone", REPO_URL, str(REPO)])
    subprocess.check_call(["git", "-C", str(REPO), "fetch", "origin", commit])
    subprocess.check_call(["git", "-C", str(REPO), "checkout", commit])
    return commit


def _pip(args: list[str], cwd: Path | None = None) -> None:
    cmd = [sys.executable, "-m", "pip", "install", "--progress-bar", "off", *args]
    print("RUN", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)


def install_deps() -> None:
    req = REPO / "requirements.txt"
    filtered = REPO / "requirements.colab.txt"
    if req.exists():
        keep = []
        for line in req.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if any(token in stripped for token in ("PyQt6", "qtpy", "ipykernel", "pytest==")):
                continue
            keep.append(line)
        filtered.write_text("\n".join(keep) + "\n", encoding="utf-8")
    if filtered.exists():
        _pip(["-r", str(filtered)], cwd=REPO)
    _pip(
        [
            "torch==2.8.0+cu128",
            "torchvision==0.23.0+cu128",
            "torchaudio==2.8.0+cu128",
            "--index-url",
            "https://download.pytorch.org/whl/cu128",
        ]
    )



def main() -> int:
    print("ST step: sha", flush=True)
    digest = require_sha()
    print("ST step: python", flush=True)
    require_python()
    print("ST step: clone", flush=True)
    commit = pin_clone()
    print("ST step: deps", flush=True)
    install_deps()
    print("ST step: env", flush=True)
    env = require_env()
    print(env, flush=True)
    group = os.environ.get("ST_GROUP_OFFLOAD", "0") == "1"
    print("ST step: inference", flush=True)
    run_inference(group)
    print("ST step: manifest", flush=True)
    write_manifest(env, commit, digest)
    print("ST done", flush=True)
    return 0


def run_inference(group_offload: bool) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(REPO / "inference" / "scripts" / "inference_psd.py"),
        "--srcp",
        str(MASTER),
        "--save_to_psd",
        "--save_dir",
        str(OUT),
    ]
    if group_offload:
        cmd.append("--group_offload")
    (OUT / "command.txt").write_text(" ".join(cmd) + "\n", encoding="utf-8")
    with (OUT / "stdout.log").open("w", encoding="utf-8") as out, (OUT / "stderr.log").open(
        "w", encoding="utf-8"
    ) as err:
        proc = subprocess.run(cmd, stdout=out, stderr=err)
    if proc.returncode != 0:
        die(proc.returncode, f"inference_psd exited {proc.returncode}")


def write_manifest(env: dict, commit: str, digest: str) -> None:
    psds = [path for path in OUT.rglob("*.psd") if "_depth" not in path.name]
    if not psds:
        psds = list(OUT.rglob("*.psd"))
    manifest = {
        "created": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "input_sha256": digest,
        "environment": env,
        "psd": [str(path) for path in psds],
    }
    (OUT / "environment.json").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if psds:
        # canonical name for download wrapper
        target = OUT / "raw.psd"
        if psds[0] != target:
            target.write_bytes(psds[0].read_bytes())


if __name__ == "__main__":
    main()
