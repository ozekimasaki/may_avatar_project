# メイ — AI-First 画像確定後パイプライン v0.3

> 前提: `mei_master_v001.png` がMASTER-FREEZE済み。  
> 目標: **See-Through以降も手描き修正をせず、AI + codeでInochi2D配信モデルまで作る。**  
> Image Repair: GPT Image 2 / Grok Imagine Image 2.0  
> Layer QA/Assembly: Python / psd-tools  
> Rig: Inochi2D / AI-generated rig recipe  
> Human role: 起動・承認・Calibrationのみ。

---

# 1. 全体

```text
MASTER-FREEZE
↓
Colab Setup
↓
See-Through
↓
Raw PSD
↓
AI Layer Audit
↓
AI Repair
↓
PSD Rebuild
↓
PSD-AI-READY
↓
AI Rig Recipe
↓
Inochi Creator / INP
↓
RIG-MVP
↓
Session + Tracker
↓
AI Calibration
↓
OBS
↓
30min Test
↓
AI Review
↓
Release
```

---

# 2. 「PSDを人間が直す」を廃止

旧:

```text
See-Through
↓
PSDを目で確認
↓
Photoshop等で手描き修正
```

新:

```text
See-Through
↓
psd-toolsで全Layer抽出
↓
AIがLayerを評価
↓
NGだけAI画像編集
↓
PythonでLayerへ反映
↓
PSD再保存
```

---

# 3. ColabのAI生成物

AIが作る:

```text
mei_see_through_v002.ipynb
```

Notebook自体も成果物。

セル:

```text
00 configuration
01 Drive mount
02 input verification
03 SHA256 verification
04 GPU
05 Python
06 clone See-Through
07 commit pin
08 dependencies
09 environment validation
10 input preview
11 inference mode
12 run inference
13 output validation
14 PSD extraction
15 contact sheet
16 automatic layer report
17 Drive export
18 log
```

---

# 4. See-Through環境

現行公式基準に合わせる。

```text
Python 3.12
PyTorch 2.8.0 + cu128
torchvision 0.23.0
torchaudio 2.8.0
```

See-Through repository commitを必ず固定。

```text
see_through_commit.txt
```

---

# 5. VRAM route

```text
>=16GB
standard

12-16GB
standard → OOMなら group_offload

10-12GB
group_offload

8-10GB
NF4 / block-swap

<8GB
別GPUを優先
```

Resolution低下は最後。

---

# 6. ST-RUN成果物

```text
02_seethrough/output/run_xxx/
├─ raw.psd
├─ composite.png
├─ environment.json
├─ command.txt
├─ stdout.log
├─ stderr.log
└─ manifest.json
```

---

# 7. Raw PSDは絶対保存

```text
03_psd/raw/mei_seethrough_raw_v001.psd
```

以後直接変更しない。

---

# 8. AI Layer Audit

`psd-tools` で全レイヤーを抽出。

```text
03_psd/audit/layers/
├─ 000_xxx.png
├─ 001_xxx.png
...
```

さらに:

```text
layer_manifest.json
contact_sheet.png
```

を自動作成。

---

# 9. Layer Manifest

各Layer:

```json
{
  "index": 0,
  "name": "",
  "bbox": [0,0,0,0],
  "visible": true,
  "opacity": 255,
  "blend_mode": "",
  "width": 0,
  "height": 0
}
```

---

# 10. AIへ渡すContact Sheet

1枚の大きなQA画像を生成する。

これは既存Layerの合成なのでAI画像生成枚数に含めない。

各tile:

```text
Layer name
Layer only
Layer + checker
Layer + nearby context
```

Vision AIが一括評価。

---

# 11. Audit JSON

AI出力:

```json
{
  "layers": [
    {
      "name": "hair_front",
      "semantic": "front_hair",
      "score": 96,
      "issues": [],
      "repair": false
    }
  ],
  "critical_issues": [],
  "repair_groups": []
}
```

---

# 12. Critical Layer

```text
Face
Eye L
Eye R
Iris L
Iris R
Mouth
Hair Front
Hair Side L/R
Hair Back
Body
Arm L/R
Apron
Skirt
```

これらを優先。

---

# 13. AIがチェックする破綻

```text
missing hidden region
wrong anatomy
duplicated finger
transparent hole
white fringe
background contamination
wrong color
changed flower
changed ribbon
stray line
seam gap
layer overlap anomaly
```

---

# 14. Repair Grouping

1 layer = 1 callにしない。

```text
Repair Group H
Head

Repair Group B
Body

Repair Group A
Accessories
```

可能なら:

```text
H + A
```

を一つにまとめる。

---

# 15. Repair Input Package

AIへ渡す1 repair package:

```text
1. master full image
2. raw layer
3. context composite
4. repair mask
5. target description
```

GPT Image 2は複数画像reference/editを利用する。

---

# 16. GPT Image 2 Repair Prompt

```text
Repair only the masked missing or corrupted region of this extracted 2D avatar layer.

The full Mei master image is the ground truth for identity, palette, line weight, clothing design and style.

The extracted layer and neighboring-context image define the exact geometry.

Fill only the missing region so the layer remains visually consistent when moved during 2D rigging.

Do not redesign any visible part.
Do not add accessories.
Do not change colors.
Do not change line thickness.
Do not move existing visible pixels unnecessarily.
Continue hidden anatomy/clothing/hair naturally behind the occluding part.
```

---

# 17. AlphaはAIに生成させない

GPT Image 2は透明背景出力前提にしない。

Repair outputから使うのは:

```text
RGB color
```

Alpha:

```text
See-Through mask
+
geometry mask
+
segmentation mask
```

からコードで作る。

---

# 18. Grok Repairへの切替

GPT Repairが2回失敗:

```text
STOP GPT
↓
Grok Image 2.0
```

Grok UIなら:

```text
Segmentation
Magic Wand
Background Removal
```

を利用可能。

APIなら自然言語image editing。

---

# 19. Grok Repair Prompt

```text
Preserve the source image exactly except for the selected/missing region.

Complete only the hidden [hair/clothing/body] area in the same chibi anime style.

Match:
- outline thickness
- brown/white/green/blue palette
- one-step cel shading
- geometry implied by the visible region

No redesign.
No new detail.
No texture.
No lighting change.
```

---

# 20. Repair Call Budget

See-Through後:

```text
Ideal    0
Normal   1
Max      2
```

3回以上必要なら:

```text
AI repairを続けない
↓
See-Through input/master構造を再評価
```

---

# 21. PSD Rebuild

Python + `psd-tools` を第一候補にする。

Workflow:

```text
open raw PSD
↓
replace repaired pixel layer data / layer image
↓
rename/reorder
↓
save new PSD
```

成果物:

```text
03_psd/final/mei_rigready_v001.psd
```

Rawは残す。

---

# 22. PSD自動命名

AIがsemantic mapを生成。

```json
{
  "raw_03": "Hair_Back",
  "raw_07": "Face",
  "raw_08": "Eye_L",
  "raw_09": "Eye_R"
}
```

Scriptでrename。

---

# 23. Rig-ready Layer Structure

```text
ROOT
├─ Back
│  └─ Hair_Back
├─ Body
│  ├─ Body_Base
│  ├─ Dress
│  ├─ Apron
│  ├─ Arm_L
│  ├─ Hand_L
│  ├─ Arm_R
│  ├─ Hand_R
│  ├─ Skirt
│  ├─ Leg_L
│  ├─ Leg_R
│  ├─ Shoe_L
│  └─ Shoe_R
├─ Head
│  ├─ Face
│  ├─ Brow_L
│  ├─ Brow_R
│  ├─ Eye_L
│  ├─ Eye_R
│  ├─ Iris_L
│  ├─ Iris_R
│  ├─ Mouth
│  ├─ Hair_Front
│  ├─ Hair_Side_L
│  ├─ Hair_Side_R
│  ├─ Ahoge
│  ├─ Headband
│  ├─ Flower
│  └─ Green_Ribbon
└─ NeckAccessory
   ├─ Blue_Ribbon
   └─ Bell
```

---

# 24. PSD-AI-READY Gate

```text
critical layer score >= 90
all required semantic layers exist
no visible holes
no severe white fringe
master identity retained
```

PASSするまでInochiへ行かない。

---

# 25. Rig RecipeをAIに作らせる

入力:

```text
rigready PSD
layer_manifest.json
master image
face atlas assets
Inochi spec
```

出力:

```text
04_inochi/rig_recipe_v001.json
```

---

# 26. Rig Recipe schema

例:

```json
{
  "nodes": [],
  "pivots": {},
  "meshes": {},
  "parameters": {},
  "bindings": {},
  "physics": {},
  "expressions": {}
}
```

---

# 27. Node Recipe

AIが座標付きで出す。

```json
{
  "name": "HeadRoot",
  "parent": "NeckRoot",
  "pivot": [768, 520],
  "children": [
    "Face",
    "Eye_L",
    "Eye_R",
    "Iris_L",
    "Iris_R",
    "Mouth",
    "Hair_Front"
  ]
}
```

座標値はPSD画像解析から計算。

---

# 28. Pivot推定

AI/CV:

```text
HeadRoot
→ 顔中心ではなく首接続付近

NeckRoot
→ 首付け根

BodyRoot
→ みぞおち〜腰

Ahoge
→ 根元

Ribbon
→ 結び目
```

画像上のpixel coordinateとして出す。

---

# 29. Mesh自動設計

輪郭からpolygon/triangulation候補をコード生成。

手順:

```text
alpha mask
↓
contour
↓
simplify
↓
interior points
↓
Delaunay triangulation
↓
mesh QA
```

AIが密度を調整。

---

# 30. Mesh density

```text
Face         medium-high
Mouth        high
Eyes         medium
Hair         medium
Body         low-medium
Accessory    low
Shoes        low
```

大量頂点を禁止。

---

# 31. Mesh QA

自動:

```text
triangle aspect ratio
edge length
outside-alpha vertices
tiny triangle count
mesh density
```

Vision:

```text
deformation test image
```

で確認。

---

# 32. Inochi Automation Route

INPはJSON payloadを含むbinary container。

そこで段階化する。

## Stage A

CreatorでPSD Import。

AIが出したRecipe通りにNode/Parameterを構築。

## Stage B

一度正常INPを作り、

```text
INP
↓
payload extractor
↓
JSON
```

して構造を学習。

## Stage C

AI-generated `inp_patch.py` でParameter等を自動生成。

---

# 33. INP Safety

INP仕様は変更可能性があるため、

```text
direct write
```

の前に毎回:

```text
backup
validate
open in Creator
```

する。

失敗したINPを元ファイルへ上書きしない。

---

# 34. MVP Parameters

最小:

```text
EyeOpen_L
EyeOpen_R
MouthOpen
MouthForm
HeadX
HeadY
HeadZ
EyeBallX
EyeBallY
```

---

# 35. Blink Source

Open:

```text
Master
```

Half / Close:

```text
Face Atlas
```

AIがAtlas patchとMaster eye geometryを整合。

---

# 36. Mouth Source

```text
Close = Master
A/I/U/E/O = Face Atlas
```

ただしInochiでは6枚切替より、

```text
MouthOpen
+
MouthForm
```

に落とす。

Atlasはkeyform設計Reference。

---

# 37. Mouth parameter

```text
MouthOpen:
0.0 close
0.3 small
0.6 normal
1.0 wide

MouthForm:
-1.0 horizontal
0.0 neutral
+1.0 round
```

AIがAtlasとの差分からkeyform geometryを提案。

---

# 38. Head parameters

順:

```text
HeadZ
HeadX
HeadY
```

SDなので可動域を抑える。

AI deformation testを出力してQA。

---

# 39. RIG-MVP Gate

```text
Blink
MouthOpen
MouthForm
HeadXYZ
EyeXY
```

のみ。

Physics禁止。

---

# 40. Session + Tracker

Trackerは1つに固定。

AIはCalibrationデータを記録。

```text
05_session/tracking_raw.csv
```

最低:

```text
neutral 10 sec
blink 10
look L/R
look U/D
mouth closed
small voice
normal voice
loud voice
```

---

# 41. AI Calibration

Scriptで:

```text
min
max
median
noise
standard deviation
```

を計算。

AIが:

```text
gain
range
deadzone
smoothing
```

を提案。

---

# 42. Mouth Noise

無言10秒。

AI:

```text
95 percentile noise
```

からdeadzone候補を出す。

人間の感覚だけで調整しない。

---

# 43. Blink Calibration

Open/Closed sampleから自動mapping。

```text
raw open median
raw closed median
```

をParameter 1/0へmapping。

---

# 44. OBS

AIが画面captureを見てQA。

評価:

```text
face readable
mouth readable
eyes readable
flower readable
outline retained
no fringe
no crop
```

---

# 45. 30分テスト

録画をAIレビュー用に区間化。

```text
00-05 normal
05-07 silent
07-10 quiet
10-13 loud
13-16 blink/look
16-20 head
20-25 normal stream
25-30 stress
```

---

# 46. AIレビュー

可能なら動画から:

```text
1 frame / 2 sec
```

程度を抽出してContact Sheet化。

全フレームをLLMへ送らない。

AIが:

```json
{
  "blink": 95,
  "mouth": 92,
  "head": 90,
  "eyes": 94,
  "stability": 98,
  "issues": []
}
```

を返す。

---

# 47. 改善ループ

NG時:

```text
画像再生成
```

へ戻らない。

問題ごとに戻り先を限定。

```text
visual layer issue → PSD repair
mesh issue         → mesh
motion issue       → keyform
noise issue        → tracking mapping
OBS issue          → capture/scale
```

---

# 48. v0.1 Image Generation Freeze

Master Freeze後は原則:

```text
full-body image generation = 0
```

PSD repairもlocal editのみ。

---

# 49. v0.2

MVP成功後:

```text
BodyX
Breath
Ahoge Physics
Hair Physics
Ribbon Physics
```

新規画像生成なし。

---

# 50. v0.3 Expressions

まずInochi parameter組合せ。

```text
Smile
Surprise
Worried
Serious
ClosedEyeSmile
```

元Character Sheetをreferenceにする。

新規画像不要。

どうしても無理な表情だけ、

```text
Expression Atlas × 1
```

を許可。

---

# 51. 最終生成枚数目標

画像確定〜v0.1:

```text
Master                1
Face Atlas            1
optional master fix   0-1
optional PSD repair   0-2
-------------------------
Target                 2
Normal                 3-4
Hard cap               6
```

---

# 52. AI-only Definition of Done

```text
No human drawing
No manual repaint
No generation spam
Reproducible prompts
Reproducible code
Pinned model/repo versions where possible
QA reports saved
Rig recipe saved
Tracking values saved
30-minute stable test
```

---

# 53. 次に実装するもの

このPlanの次の実装物は:

```text
1. character_spec.yaml generator
2. prompt_master_v001.txt
3. master_qa.py
4. generation_log.csv
5. G001 master 1枚
```

まだFace Atlasを生成しない。

まずMasterを1枚で決める。
