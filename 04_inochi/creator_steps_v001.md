# Creator Stage A — 人間が GUI で踏む手順

Inochi Creator **v0.8.6**（`tools/inochi-creator/` の zip 展開）。Nightly 禁止。`win32` は Win32 API であり 32bit ではない。

起動前バックアップ:

1. `04_inochi/working/` に既存 `.inp` があれば `04_inochi/backups/` へコピーしてから開く。
2. 失敗した INP を元ファイルへ上書きしない。

## Stage A

1. `scripts/install_inochi_windows.ps1` 済みであること。
2. Creator を起動する。起動直後の Thank you ナグは Close。
3. File → Import → Photoshop Document で `03_psd/final/mei_rigready_v001.psd` を読む。ImGui のためアクセシビリティ木が空で、エージェントの自動クリックはモニター跨ぎで外れる。ここだけ人間。
4. `04_inochi/rig_recipe_v001.json` の Node / Pivot を再現する。
   - HeadRoot = 首接続。顔中心に置かない。
   - NeckRoot = 付け根。
   - BodyRoot = みぞおち〜腰。
   - Ahoge = 根元。
   - Ribbon = 結び目。
5. Parameters のみ作る（Physics は空）:
   - EyeOpen_L / EyeOpen_R
   - MouthOpen (0 / 0.3 / 0.6 / 1.0)
   - MouthForm (-1 / 0 / +1)
   - HeadX / HeadY / HeadZ（適用順 HeadZ → X → Y）
   - EyeBallX / EyeBallY
6. Blink Open = Master。Half / Close = Atlas 抽出パッチ。
7. Mouth close = Master。A/I/U/E/O = Atlas。
8. 保存先: `04_inochi/working/mei_mvp.inp`
9. Blink / Mouth / Head / Eye が動いたスクショを `07_reviews/reports/RIG-MVP/` に置く。

## Stage B（v0.2）

正常 INP から payload を抽出し、BodyX / Breath / Ahoge / Hair / Ribbon Physics を足す。新規画像 0。

## Stage C（v1.0）

backup → validate → Creator。`08_repro/pins.yaml` と `scripts/repro_check.py`。
