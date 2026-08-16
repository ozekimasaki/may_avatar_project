---
name: mei-rig-stage-a
description: >-
  Inochi Creator Stage A 指示書。RIG-MVP、ノード、パラメータ、まばたき、口形、
  may.inx 保存、Creator スクショのときに使う。Physics は触らない。
---

# mei-rig-stage-a

正本は [`04_inochi/creator_steps_v001.md`](mdc:04_inochi/creator_steps_v001.md)。そこの順を守る。別手順を作らない。

## いまの前提

色付き PSD（`03_psd/final/mei_rigready_v001.psd`）の Import は済み。次はリグを組んで動かして保存する。

## 順

1. ノード。HeadRoot は顔の真ん中ではなく首の付け根。その下に Face / 目 / 口 / 前髪 / Ahoge
2. パラメータだけ作る（Physics は触らない）。EyeOpen_L EyeOpen_R MouthOpen MouthForm HeadX HeadY HeadZ EyeBallX EyeBallY
3. テクスチャ。まばたき Open は今の Master。Half / Close は `01_art/face_atlas/extracted/` の `eye_half.png` と `eye_close.png`。口の Close は Master、A/I/U/E/O は同じフォルダの `mouth_*.png`
4. 上書き保存（`04_inochi/working/may.inx` でよい）。既存があれば先に `04_inochi/backups/` へコピー。失敗したファイルを元ファイルへ上書きしない
5. 目・口・頭が動いている画面を 4 枚、`07_reviews/reports/RIG-MVP/` に置く（`blink.png` `mouth.png` `head.png` `eyes.png`）

## 禁止

- Physics
- INP/INX の捏造
- MASTER-FREEZE 後の全身再生成
