#!/usr/bin/env bash
# WSL only. Always stop mei-st-run, even on error. No Drive. No interactive auth.
set -euo pipefail

SESSION="${SESSION:-mei-st-run}"
ROOT="${ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
RUN_ID="${RUN_ID:-run_$(date +%Y%m%dT%H%M%S)}"
OUT="$ROOT/02_seethrough/output/$RUN_ID"
MASTER="$ROOT/01_art/master/mei_master_v001.png"
SHA="$ROOT/01_art/master/mei_master_v001.sha256"
COMMIT="$ROOT/02_seethrough/see_through_commit.txt"
RUNNER="$ROOT/02_seethrough/run_seethrough.py"
GPU="${GPU:-L4}"

mkdir -p "$OUT"

cleanup() {
  colab stop -s "$SESSION" || true
}
trap cleanup EXIT

if ! command -v colab >/dev/null 2>&1; then
  echo "colab CLI missing. Install in WSL: uv tool install google-colab-cli" >&2
  exit 2
fi

start_session() {
  local gpu="$1"
  colab new -s "$SESSION" --gpu "$gpu"
}

if ! start_session "$GPU"; then
  if [[ "$GPU" == "L4" ]]; then
    GPU=T4
    start_session "$GPU"
  else
    exit 3
  fi
fi

colab upload -s "$SESSION" "$MASTER" /content/mei_master_v001.png
colab upload -s "$SESSION" "$SHA" /content/mei_master_v001.sha256
colab upload -s "$SESSION" "$COMMIT" /content/see_through_commit.txt
colab exec -s "$SESSION" -f "$RUNNER" --timeout 7200

colab download -s "$SESSION" /content/output/raw.psd "$OUT/raw.psd" || true
colab download -s "$SESSION" /content/output/manifest.json "$OUT/manifest.json" || true
colab download -s "$SESSION" /content/output/environment.json "$OUT/environment.json" || true
colab download -s "$SESSION" /content/output/command.txt "$OUT/command.txt" || true
colab download -s "$SESSION" /content/output/stdout.log "$OUT/stdout.log" || true
colab download -s "$SESSION" /content/output/stderr.log "$OUT/stderr.log" || true
colab log -s "$SESSION" -o "$OUT/colab_log.md" || true

if [[ -f "$OUT/raw.psd" ]]; then
  cp "$OUT/raw.psd" "$ROOT/03_psd/raw/mei_seethrough_raw_v001.psd"
  chmod a-w "$ROOT/03_psd/raw/mei_seethrough_raw_v001.psd" || true
  sha256sum "$ROOT/03_psd/raw/mei_seethrough_raw_v001.psd" | awk '{print $1}' > "$ROOT/03_psd/raw/mei_seethrough_raw_v001.sha256"
fi
