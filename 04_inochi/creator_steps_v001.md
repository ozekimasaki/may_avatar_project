# Creator Stage A 指示書

Inochi Creator **v0.8.6**（`tools/inochi-creator/`）。Nightly 禁止。`win32` は Win32 API であり 32bit ではない。

色付き PSD の Import は済み。ここからは **リグを組んで動かして保存** する。

## 禁止

- Physics を触らない（空のまま）
- 失敗したファイルを元ファイルへ上書きしない
- 上書き保存の前に `04_inochi/backups/` へコピーする
- 全身画像の再生成をしない

## 入力

| 用途 | パス |
| --- | --- |
| 読み込み済み PSD | `03_psd/final/mei_rigready_v001.psd` |
| ノード座標の正本 | `04_inochi/rig_recipe_v001.json` |
| まばたき Half | `01_art/face_atlas/extracted/eye_half.png` |
| まばたき Close | `01_art/face_atlas/extracted/eye_close.png` |
| 口 A/I/U/E/O | `01_art/face_atlas/extracted/mouth_a.png` など |
| 保存先 | `04_inochi/working/may.inx` |
| スクショ置き場 | `07_reviews/reports/RIG-MVP/` |

まばたき Open と口 Close は Import 済み Master のまま。Atlas で置き換えない。

## 手順

Creator でこの順にやる。

### 1. ノード

HeadRoot は顔の真ん中ではなく **首の付け根**。その下に Face / 目 / 口 / 前髪 / Ahoge。

`rig_recipe_v001.json` の Pivot を使う。

- HeadRoot = 首接続。顔中心に置かない
- NeckRoot = 付け根
- BodyRoot = みぞおち〜腰
- Ahoge = 根元
- Ribbon = 結び目

HeadRoot の子:

- Face
- Eye_L / Eye_R
- Iris_L / Iris_R
- Mouth
- Hair_Front
- Ahoge

### 2. パラメータだけ作る（Physics は触らない）

- EyeOpen_L
- EyeOpen_R
- MouthOpen（キー 0 / 0.3 / 0.6 / 1.0）
- MouthForm（キー -1 / 0 / +1）
- HeadX
- HeadY
- HeadZ（適用順 HeadZ → HeadX → HeadY）
- EyeBallX
- EyeBallY

### 3. テクスチャ

- まばたき Open は今の Master
- Half / Close は `01_art/face_atlas/extracted/` の `eye_half.png` と `eye_close.png`
- 口の Close は Master
- A / I / U / E / O は同じフォルダの `mouth_a.png` `mouth_i.png` `mouth_u.png` `mouth_e.png` `mouth_o.png`

### 4. 上書き保存

保存先は `04_inochi/working/may.inx` でよい。

既存ファイルがあるときは、先に `04_inochi/backups/` へコピーしてから上書きする。

### 5. スクショ 4 枚

目・口・頭が動いている画面を 4 枚、`07_reviews/reports/RIG-MVP/` に置く。

| ファイル | 内容 |
| --- | --- |
| `blink.png` | EyeOpen でまばたき |
| `mouth.png` | MouthOpen / MouthForm |
| `head.png` | HeadX / HeadY / HeadZ |
| `eyes.png` | EyeBallX / EyeBallY |

## 完了条件

- `04_inochi/working/may.inx` がある
- 上記 4 枚がある
- Physics は空
- HeadRoot が顔中心ではない

揃ったら `python scripts/run_tests.py --gate RIG-MVP` のあと gate review。

## Stage B（v0.2）

正常な保存ファイルから payload を抽出し、BodyX / Breath / Ahoge / Hair / Ribbon Physics を足す。新規画像 0。

## Stage C（v1.0）

backup → validate → Creator。`08_repro/pins.yaml` と `scripts/repro_check.py`。
