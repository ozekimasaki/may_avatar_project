# メイ — GPT Image 2 / Grok Image 2.0 最小画像生成計画 v0.3

> 目的: **配信用モデルに必要な画像資産を、最少のAI画像出力で作る。**  
> Primary: `gpt-image-2`  
> Secondary: `grok-imagine-image-2.0`  
> Baseline画像出力: **2枚**  
> Full-body generation hard cap: **2枚**  
> MVPではExpression画像を追加生成しない。

---

# 1. 入力

既存参照:

```text
00_reference/mei_character_sheet.png
```

内容:

- 正面
- 横
- 後
- 表情
- 髪
- 目
- 花/リボン
- メイド服
- エプロン
- 首リボン/鈴
- 靴
- 配色

これを新規生成せず、そのままreferenceにする。

---

# 2. 生成資産を2枚に圧縮する

旧方式:

```text
Master                  1
Mouth Close/A/I/U/E/O   6
Eye Open/Half/Close     3
Expression              5
--------------------------
15画像程度
```

新方式:

```text
Master                  1
Face Atlas              1
--------------------------
2画像
```

---

# 3. G001 — Master

Filename:

```text
mei_master_v001.png
```

Primary:

```text
gpt-image-2
```

Reference:

```text
mei_character_sheet.png
```

目的:

> See-Throughにそのまま渡せる、完全正面・全身・口閉じの唯一の基準画像。

---

# 4. Master Canvas

第一候補:

```text
1024 x 1536
```

理由:

- GPT Image 2のportrait生成に適したサイズ
- See-Throughの入力として十分
- 生成/編集コストを無駄に上げない

MASTER-FREEZE後に必要ならコードで作業用サイズへ変換する。

最初から4K生成しない。

---

# 5. Master Prompt Architecture

Promptを5 blockに分ける。

```text
A. Identity
B. Geometry
C. Art style
D. Rig constraints
E. Forbidden changes
```

---

# 6. A — Identity

```text
Create one chibi anime character based strictly on the attached Mei character design reference.

Character identity:
- short warm brown bob haircut
- one prominent ahoge
- bright green eyes
- white maid headband
- white primrose-like flower ornament
- green ribbon hair ornament
- brown maid dress
- clean white apron
- blue-green neck bow
- gold bell at the neck
- dark green tights
- brown Mary Jane strap shoes

Preserve the same recognizable character identity, palette, hairstyle, accessories, and clothing design from the reference.
```

---

# 7. B — Geometry

```text
Exactly one character.
Full body.
Perfect straight front view.
Camera centered at character center.
No perspective turn.
Head upright.
Shoulders level.
Hips level.
Eyes looking directly forward.
Both arms hanging naturally but separated slightly from the torso.
A visible strip of background between each arm and the body.
Both hands fully visible.
Hands must not overlap the skirt or apron.
Both legs slightly separated.
A visible strip of background between the legs.
Both shoes entirely inside the frame.
```

---

# 8. C — Art Style

```text
Super-deformed chibi proportions suitable for 2D avatar rigging.
Bold, clean, smooth anime outlines.
Simple flat cel shading.
One simple shadow level.
Large readable facial features.
Simple grouped hair shapes.
Minimal fine detail.
Clean silhouette.
No painterly texture.
No complex lighting.
```

---

# 9. D — Rig Constraints

```text
Design for semantic layer separation and 2D rigging:
- front hair must read separately from side hair
- side hair must read separately from shoulders
- ahoge must have a clean isolated silhouette
- flower and green ribbons must have readable boundaries
- apron boundary must be clearly visible against the brown dress
- sleeves must read separately from arms/hands
- left and right legs must not visually merge
- avoid tiny frills or thin loose strands
```

---

# 10. E — Forbidden

GPT Imageには別negative prompt欄を前提にせず、本文へ明示する。

```text
Do not create:
- side view
- three-quarter view
- head tilt
- dynamic pose
- bent torso
- crossed legs
- crossed arms
- hands behind body
- hands touching skirt
- cropped feet
- cropped ahoge
- props
- text
- labels
- extra characters
- background objects
- cast shadow
- detailed scenery
- gradient background
- extra hair ornaments
- changed clothing colors
- changed eye color
```

---

# 11. Master Expression

```text
Both eyes open.
Neutral eyebrows.
Closed mouth.
Very subtle friendly smile.
No teeth.
No open mouth.
```

理由:

差分の基準にするため。

---

# 12. Background

GPT Image 2は透明背景を使わない。

Masterは:

```text
flat pure/near-white background
```

でよい。

See-Through用にも単純背景が都合がよい。

---

# 13. G001生成後は即QA

2枚目の候補を生成する前に必ずQA。

AIがJSONで返す。

```json
{
  "hard_fail": [],
  "soft_fail": [],
  "scores": {
    "identity": 0,
    "front_view": 0,
    "symmetry": 0,
    "arm_separation": 0,
    "leg_separation": 0,
    "hair_separation": 0,
    "clothing_separation": 0,
    "readability": 0
  },
  "total": 0,
  "decision": ""
}
```

---

# 14. Score

```text
Identity             25
Front view           15
Symmetry             10
Arms                  10
Legs                  10
Hair separation      10
Clothing separation  10
Readability           5
Background            5
```

100点。

---

# 15. Master Decision Tree

```text
hard_fail == 0
AND score >= 90
    ↓
FREEZE
```

```text
hard_fail == 0
AND score 80-89
    ↓
MASK EDIT
```

```text
hard_fail >= 1
    ↓
構造的失敗か?
  ├ yes → Full Retry 1回
  └ no  → MASK EDIT
```

---

# 16. Full Retryは1回まで

Master全身生成は:

```text
G001
+
必要ならG001R
```

のみ。

`G001R` もHard Failなら、

```text
promptを変えてガチャ
```

ではなく、

```text
良い方を選ぶ
+
Grok/GPT local edit
```

へ移行する。

---

# 17. Local Edit優先順位

まず `gpt-image-2` mask edit。

対象例:

```text
口
花
リボン
手
腕の隙間
脚の隙間
前髪
```

編集Promptには必ず:

```text
Modify only the masked region.
Preserve every unmasked element exactly.
Keep the character identity, pose, proportions, colors, line thickness, lighting, and all other pixels visually unchanged.
```

を入れる。

---

# 18. GPT Editが直らない場合

同一箇所:

```text
GPT edit #1
↓ NG
GPT edit #2
↓ NG
STOP
```

3回目GPTをしない。

次:

```text
Grok Image 2.0
```

へ切り替える。

---

# 19. Grok Repair

grok.comのImage 2.0 Quality Modeが利用可能なら:

```text
Magic Wand
または
Segmentation
```

で局所を選択。

Instruction:

```text
Keep everything outside the selected region unchanged.
Match the exact chibi line art, color palette, cel shading, proportions, and design of the existing character.
Only repair [issue].
```

API利用の場合:

```text
model = grok-imagine-image-2.0
```

inputにMasterを渡し自然言語edit。

---

# 20. MASTER-FREEZE

Pass後:

```text
01_art/master/mei_master_v001.png
01_art/master/mei_master_v001.sha256
01_art/master/master_qa_v001.json
```

SHA256を記録。

以後Full-body generation禁止。

---

# 21. G002 — Face Atlas

次に生成する唯一の基本追加画像。

```text
mei_face_atlas_v001.png
```

目的:

```text
口 A/I/U/E/O
+
Half Eye
+
Closed Eye
```

を1枚から得る。

Masterにあるもの:

```text
Closed Mouth
Open Eye
```

は再生成不要。

---

# 22. Face Atlas設計

1枚の画像を9セルにする。

```text
┌──────┬──────┬──────┐
│ A    │ I    │ U    │
├──────┼──────┼──────┤
│ E    │ O    │ HALF │
├──────┼──────┼──────┤
│CLOSE │BROW? │SPARE │
└──────┴──────┴──────┘
```

実際の抽出対象:

```text
A
I
U
E
O
Eye Half
Eye Close
```

余りセルは無理に使わない。

---

# 23. Atlas方式

安定性優先で、

> 「孤立した口だけを描く」

より、

> 「同一顔cropを並べ、変更点だけ変える」

を第一候補にする。

各セル:

```text
same face geometry
same hair edge if visible
same nose
same skin tone
same cheek
different mouth OR eyelid only
```

あとでimage registrationして差分を抽出する。

---

# 24. Atlas Reference

Input:

```text
1. mei_master_v001.png
2. mei_character_sheet.png の表情領域
```

必要ならMasterから顔cropを事前作成:

```text
mei_master_face_crop_v001.png
```

これは生成画像ではなくcropなので枚数Budgetに含めない。

---

# 25. Face Atlas Prompt

```text
Using the attached Mei master face as the exact identity and geometry reference, create a clean facial-expression reference atlas.

Every cell must show the exact same character, same head shape, same eye size, same iris color, same hairstyle, same skin tone, same line weight, same camera angle, and same facial proportions.

Only the requested mouth or eyelid shape changes.

Required mouth states:
A: wide natural open vowel
I: narrow horizontal open shape
U: small rounded shape
E: medium horizontal shape
O: larger rounded shape

Required eye states:
Half: natural halfway blink
Closed: clean relaxed closed-eyelid line

No teeth unless minimally required.
No tongue unless minimally required.
No head movement.
No gaze movement.
No eyebrow change.
No cheek change.
No hairstyle change.
No accessory change.
Flat simple background.
Clear equal-sized cells.
```

---

# 26. Atlas QA

AI/Scriptで検査。

- Face alignment
- Eye center distance
- Iris size
- head crop scale
- line weight consistency
- skin color difference
- only intended region difference

各セルをMaster顔へregistration。

---

# 27. Atlas Extraction

Python:

```text
atlas
↓
cell crop
↓
face registration
↓
difference map
↓
mouth/eye ROI
↓
alpha mask
↓
feature patch
```

生成し直さずコードで抽出。

---

# 28. 必要なFace Assets

```text
mouth_close = Master
mouth_a
mouth_i
mouth_u
mouth_e
mouth_o

eye_open = Master
eye_half
eye_close
```

実質新規描画:

```text
G002一枚
```

のみ。

---

# 29. Atlas失敗時

一部セルだけNGでもG002を丸ごと再生成しない。

例:

```text
A OK
I OK
U NG
E OK
O OK
Half OK
Close OK
```

なら、

```text
Uだけlocal edit
```

する。

---

# 30. Atlas全体が不安定な場合

G002が構造的に失敗した場合だけ:

```text
G002R
```

を1回許可。

それ以上は禁止。

代替:

```text
mouth atlas
eye atlas
```

へ2枚に分ける判断もあるが、
これは最終手段。

---

# 31. Expression Referenceは作らない

MVPでは:

```text
smile.png
surprise.png
worried.png
serious.png
closed_eye_smile.png
```

を生成しない。

元のCharacter Sheetにすでに表情参考がある。

それをInochi変形のReferenceにする。

---

# 32. See-Through補修画像Budget

See-Through後に欠損が出た場合も、
1パーツ1生成にしない。

NGを:

```text
Head Repair Set
Body Repair Set
```

へまとめる。

最大:

```text
2 AI repair outputs
```

を目標。

---

# 33. 最終画像出力数目標

Ideal:

```text
G001 Master       1
G002 Face Atlas   1
-------------------
2
```

Normal:

```text
Master            1
Master edit       1
Face Atlas        1
PSD repair        1
-------------------
4
```

Hard Cap目安:

```text
6
```

6を超えそうなら、

> 生成不足ではなくPipeline/Prompt/分解方法に問題がある

と判定して設計を見直す。

---

# 34. 最重要ルール

```text
「惜しいからもう1枚」
```

は禁止。

代わりに:

```text
何がNGか
↓
Hard/Soft分類
↓
Softなら局所修正
↓
HardだけFull Retry
```

とする。

---

# 35. 直近タスク

1. Character Sheetから `character_spec.yaml` をAIで作る。
2. `prompt_master_v001.txt` を固定。
3. GPT Image 2で **1枚だけ** Masterを生成。
4. QA。
5. PASSなら即凍結。
