# メイ配信用アバター

AI-first で Inochi2D 配信用モデルを作る。手描き修正と全身ガチャは禁止。既存の Character Sheet と Master 候補は凍結済み。

正本:

- [docs/mei_ai_first_master_plan_v003.md](docs/mei_ai_first_master_plan_v003.md)
- [docs/mei_image_generation_ai_minimal_v003.md](docs/mei_image_generation_ai_minimal_v003.md)
- [docs/mei_ai_after_image_pipeline_v003.md](docs/mei_ai_after_image_pipeline_v003.md)

公開リポジトリ: https://github.com/ozekimasaki/may_avatar_project  
`.env` は追跡しない。`KIE_API_KEY` をローカルに置く。

## 予算

v0.1 画像生成 hard cap は **6**。MASTER-FREEZE 後の全身再生成は **0**。Face Atlas は 1 枚。PSD repair は最大 2 call。

## Gate

各 Gate は `自動テスト → 仕様再評価レビュー → 人間承認` の3段。失敗したら同じテスト ID を全部やり直す。前回 PASS は流用しない。

| Gate | 内容 |
| --- | --- |
| SPEC-FREEZE | 骨格・spec・prompt・log |
| MASTER-FREEZE | 既存 `avatar_base.png` の QA。画像は作らない |
| FACE-ASSET-FREEZE | Atlas 1枚 + 抽出 |
| ST-RUN | Colab CLI で See-Through。必ず `colab stop` |
| PSD-AI-READY | audit / repair≤2 / rebuild |
| RIG-MVP | recipe + mesh + Creator Stage A |
| TRACK-OK | tracking CSV + calibration |
| OBS-OK | 配信スクショ QA |
| RELEASE-v0.1 | 30分安定 |
| RELEASE-v0.2 | 物理。新規画像 0 |
| RELEASE-v0.3 | 表情パラメータ |
| RELEASE-v1.0 | pins と再現チェック |

定義は [`07_reviews/gates.yaml`](07_reviews/gates.yaml)。

## セットアップ

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

テスト:

```text
python scripts/run_tests.py --gate SPEC-FREEZE
python scripts/review_gate.py --gate SPEC-FREEZE
```

See-Through は Windows ネイティブ非対応。WSL2 から [`scripts/st_run_colab.sh`](scripts/st_run_colab.sh) を使う。Drive マウントと `colab auth` は使わない。

Inochi Creator は v0.8.6 の zip を `tools/` へ展開する（gitignore）。`win32` は Win32 API であり 32bit ではない。
