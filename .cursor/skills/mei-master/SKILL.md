---
name: mei-master
description: >-
  Mei streaming avatar pipeline rules: gate order, image budget, no full-body
  regen after MASTER-FREEZE, no extra generations because it looks almost cute.
  Use when working on this repo, KIE calls, See-Through, PSD, Inochi, or releases.
---

# mei-master

正本は `docs/` の v003 三本。既存 `character_sheet.png` と `avatar_base.png` は再生成しない。

## Gate 順

SPEC-FREEZE → MASTER-FREEZE → FACE-ASSET-FREEZE → ST-RUN → PSD-AI-READY → RIG-MVP → TRACK-OK → OBS-OK → RELEASE-v0.1 → v0.2 → v0.3 → v1.0

飛ばさない。各 Gate は `python scripts/run_tests.py --gate <GATE>` → `mei-gate-review` → 人間承認。

## 予算

- v0.1 cap **6**（`scripts/budget.py`）
- MASTER-FREEZE 後の全身生成 **0**
- 「あと一枚で可愛くなる」は禁止
- Face Atlas は 1 枚。セル NG はセル edit。G002R は構造失敗 1 回
- PSD repair 最大 2。RGB=KIE、alpha=コード

## 戻り先（§47）

全文生図に戻らない。

- visual / fringe / hole → PSD-AI-READY repair
- mesh → RIG-MVP mesh
- motion / keyform → RIG-MVP parameter
- tracking noise → TRACK-OK
- OBS crop/scale → OBS-OK
- Face 差分 → FACE-ASSET-FREEZE セル edit
- Master identity 崩壊 → STOP

## 人間だけがやること

Creator GUI、カメラ Calibration、Gate 最終承認、UAC 許可、「かわいい」判定。手描き禁止。

## See-Through

Skill `google-colab-cli`。Windows は WSL。`colab auth` / `drivemount` / TTY `repl` 禁止。セッション `mei-st-run`。終わったら必ず `colab stop`。
