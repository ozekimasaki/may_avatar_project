# メイ AI-First 配信用アバター制作 — Master Plan v0.3

> 更新日: 2026-08-16  
> 目的: **人間が絵を描かず、AIを制作主体として、配信用Inochi2Dアバター「メイ」を完成させる。**  
> 画像生成モデル: `gpt-image-2` / `grok-imagine-image-2.0`  
> レイヤー分解: See-Through  
> リグ: Inochi Creator / Inochi2D  
> 配信: Inochi Session + Tracker + OBS  
> 重要方針: **生成枚数を増やすのではなく、1つの確定資産をAI編集・AI補完・コード処理で育てる。**

---

# 1. プロジェクトの定義

このプロジェクトにおける「AIですべて作る」は次を意味する。

## AIが担当するもの

- キャラクター画像生成
- キャラクター画像修正
- 口・目の差分設計
- レイヤー分解
- 隠れ領域補完
- PSDレイヤーQA
- PSD修復案
- PSDの機械的再構築
- Inochi2Dリグ設計
- Pivot座標推定
- Mesh設計
- Parameter設計
- Tracking Mapping案
- Colab Notebook生成
- Pythonスクリプト生成
- QAコード生成
- ログ解析
- テスト結果レビュー
- 改善案生成

## 人間が担当してよいもの

人間は「制作」ではなくオペレーターと最終承認者。

- APIキーを用意する
- Colabを起動する
- AI案を承認/却下する
- Inochi Creatorを起動する
- 必要なGUI操作を実行する
- カメラの前でCalibrationする
- 最終的に「かわいい/メイらしい」を判断する

## 原則やらないもの

- 手描き修正
- ペンタブで描き足す
- Photoshopで手塗り
- 口を1枚ずつ人間が描く
- 目を1枚ずつ人間が描く
- AI出力のたびに全身を再生成する
- 何十枚も候補を作ってガチャする

---

# 2. AI役割分担

## Orchestrator AI

担当:

```text
仕様管理
Prompt生成
画像QA
コード生成
ログ解析
Gate判定
次アクション決定
```

出力例:

```text
prompt_master_v001.txt
qa_master_v001.json
repair_request_001.json
rig_recipe_v001.json
tracking_calibration.md
```

---

# 3. GPT Image 2 の担当

モデル:

```text
gpt-image-2
```

再現性が必要になったら、利用可能なsnapshotを固定する。

主担当:

```text
1. 最初のマスター画像
2. マスターを基準にした高忠実度編集
3. maskを使った局所修正
4. 顔パーツAtlas生成
5. See-Through後の隠れ部分のAI補完
```

理由:

- image input/outputに対応
- image editに対応
- mask editに対応
- gpt-image-2は入力画像を高忠実度で扱う
- マスターを固定して育てる用途と相性が良い

注意:

```text
gpt-image-2 は透明背景出力を現在サポートしない
```

したがって透明化はモデルに任せない。

```text
AI画像
+
既存alpha/mask
+
Python合成
```

で作る。

---

# 4. Grok Imagine Image 2.0 の担当

モデル:

```text
grok-imagine-image-2.0
```

主担当:

```text
1. GPT Image 2で局所修正が安定しない場合の第二編集器
2. Grok UIのMagic Wandによる局所編集
3. Segmentation
4. Background removal
5. 複数referenceを使った補修
```

重要:

> 同じ箇所をGPT→GPT→GPTと何度も生成しない。

修正が1〜2回で収束しない場合、

```text
GPT Image 2
↓
Grok Image 2.0
```

へモデルを切り替える。

「別モデルに変える」ことを生成枚数削減策として利用する。

---

# 5. 生成枚数Budget

## Baseline

プロジェクト前半で本当に新規生成する画像は原則2枚。

```text
G001  mei_master_v001.png
G002  mei_face_atlas_v001.png
```

これだけ。

---

# 6. Full Generation Hard Cap

See-Through開始前:

```text
理想     2画像
通常上限 3画像
絶対上限 4画像
```

3枚目/4枚目は失敗時だけ。

例:

```text
G001 master
G002 face atlas

必要なら
G003 master retry OR atlas retry

緊急時のみ
G004 model-switch repair
```

---

# 7. 「生成」と「編集」を分ける

新しい全身画像を作る操作:

```text
FULL GENERATION
```

マスターの一部だけを変える操作:

```text
LOCAL EDIT
```

このプロジェクトでは、

```text
FULL GENERATIONを極端に減らす
```

ことを最優先する。

LOCAL EDITも無制限には行わない。

同じ問題に:

```text
最大2 edit
```

まで。

2回で直らなければPromptではなく方法を変える。

---

# 8. 既存参照画像

現在の三面図+表情集を、

```text
00_reference/mei_character_sheet.png
```

として唯一のデザイン基準資料にする。

ここから読み取るもの:

```text
髪
目
花
緑リボン
メイドカチューシャ
茶ドレス
白エプロン
青首リボン
鈴
ストッキング
靴
全体の色
表情傾向
```

参照画像自体はSee-Throughへ入れない。

---

# 9. Assets Flow

```text
Character Sheet
      ↓
AI extracts Character Spec
      ↓
character_spec.yaml
      ↓
GPT Image 2
      ↓
Master × 1
      ↓
AI QA
      ↓
local edit only if needed
      ↓
MASTER-FREEZE
      ↓
Face Atlas × 1
      ↓
Auto crop / mask / register
      ↓
Face Assets
      ↓
See-Through
      ↓
Layered PSD
      ↓
AI Layer Audit
      ↓
AI repair only failed regions
      ↓
Rig-ready PSD
      ↓
AI Rig Recipe
      ↓
Inochi2D
      ↓
Session / Tracker
      ↓
AI calibration review
      ↓
OBS
```

---

# 10. Gate設計

```text
SPEC-FREEZE
MASTER-FREEZE
FACE-ASSET-FREEZE
ST-RUN
PSD-AI-READY
RIG-MVP
TRACK-OK
OBS-OK
RELEASE-v0.1
```

Gateを通るまでは次へ進まない。

---

# 11. AIの修正判断

全工程共通。

```text
Hard Fail
→ 作り直す/構造を変える

Soft Fail
→ 局所編集

No Fail
→ 触らない
```

「もっとよくできそう」は再生成理由にしない。

---

# 12. Hard Failの例

Master:

- 正面でない
- 全身が切れている
- 腕が完全に胴体と融合
- 脚が1本に見える
- 手指が大破綻
- デザインが参照と別キャラ
- 目が左右で大きく異なる

これだけがFull Generation retry候補。

---

# 13. Soft Failの例

- 花位置が少しずれた
- 青リボンが少し大きい
- 口が微笑みすぎ
- 前髪1束だけ不自然
- 腕の隙間が少し狭い

これはFull Generation禁止。

Mask editで直す。

---

# 14. AI QAは画像生成しない

QAに使うのは:

```text
Vision LLM
OpenCV
Pillow
NumPy
edge detection
symmetry metrics
pixel diff
PSD structure parser
```

画像を何枚も作らず、既存画像を評価する。

---

# 15. プロンプトのVersion管理

```text
00_reference/prompts/
├─ master_v001.txt
├─ master_repair_v001.txt
├─ face_atlas_v001.txt
├─ psd_head_repair_v001.txt
└─ psd_body_repair_v001.txt
```

プロンプト変更も履歴を残す。

---

# 16. Generation Log

```text
01_art/generation_log.csv
```

Columns:

```text
id
timestamp
model
mode
input
prompt_version
output
purpose
accepted
reason
next_action
```

例:

```text
G001,gpt-image-2,FULL,...,accepted
E001,gpt-image-2,EDIT,...,accepted
G002,gpt-image-2,FULL,...,accepted
```

---

# 17. AI画像作業の停止条件

新規画像を増やさないために停止条件を明示。

## Master

```text
score >= 90
AND hard_fail_count == 0
```

で即Freeze。

95→98を目指して生成し直さない。

## Face Atlas

```text
必要なmouth/eye shapeが抽出可能
```

ならFreeze。

「シート自体が美しい」は不要。

---

# 18. 表情素材

MVPでは新規生成しない。

```text
Smile
Surprise
Worried
Serious
EyesClosedSmile
```

は、

```text
Brows
EyeOpen
MouthOpen
MouthForm
Head/face deformation
```

の組合せでInochi側で作る。

どうしても形が足りなければ v0.3 で1枚のExpression Atlasを追加。

---

# 19. AI-only PSD方針

See-Through Raw PSDをAIで分析。

```text
PSD
↓
psd-tools
↓
全レイヤーPNG化
↓
contact sheet
↓
Vision AI audit
↓
NG layerだけrepair
↓
PythonでPSDへ戻す
```

人間による手描き修正を挟まない。

---

# 20. AI repairの単位

一つずつ大量に呼ばない。

NGを:

```text
HEAD
BODY
ACCESSORY
```

の3群へまとめる。

1回のrepair callで可能な限りまとめる。

---

# 21. Inochi2D AI化

Inochi2DのINPは、

```text
Binary Container
+
JSON Rig Payload
+
Textures
```

という構造を持つ。

そのため最終目標は、

> AIが `rig_recipe.json` を生成し、コードがINP/Creator操作へ変換する

こと。

---

# 22. Rig Automationの2段階

## v0.1 Safe Route

AI:

- Node構造を決める
- Pivotを画像から推定
- Mesh密度を決める
- Parameterキーを決める
- keyform値を設計
- 操作手順を出す

人間:

- Creator GUI上で実行

制作判断はAI。

## v0.2 Automation Route

AIが:

```text
INP spec
+
Creator出力sample
```

を解析。

```text
rig_recipe.json
↓
inp_builder / inp_patch script
↓
model.inp
↓
Creatorでvalidation
```

へ進める。

---

# 23. なぜ最初からINP直生成しないか

Inochi2DのINP仕様は1.0以前で変更可能性がある。

したがって、

```text
まずCreatorで正常に開くsampleを1個作る
↓
AIがpayload差分を学ぶ
↓
自動化
```

の順にする。

生成枚数削減と同じく、

> 一度正しい基準を作り、それを変形する

思想をリグにも適用する。

---

# 24. 人間の作業削減目標

v0.1:

```text
人間
= 実行/承認/GUI操作
```

v0.2:

```text
人間
= 実行/承認
```

v1.0:

```text
人間
= 最終承認/Calibration
```

---

# 25. リリース定義

v0.1:

```text
見た目固定
Blink
Mouth
Head XYZ
Eye XY
Session
OBS
30分安定
```

v0.2:

```text
AI rig automation増加
Body
Breath
Hair Physics
```

v0.3:

```text
Expressions
Hotkeys
AI calibration tuning
```

v1.0:

```text
再現可能なAI Pipeline
```

---

# 26. 完成の定義

このプロジェクトは、

> 「AIで可愛い絵を大量に生成した」

ことが成功ではない。

成功は:

```text
1つの参照
↓
少数生成
↓
AIが資産を育てる
↓
再現可能なPipelineになる
↓
メイが配信で自然に動く
```

こと。

---

# 27. 直近の実行順

```text
01 Character SpecをAIで構造化
02 Master Prompt固定
03 GPT Image 2でMasterを1枚だけ生成
04 AI QA
05 必要な場合だけmask edit
06 MASTER-FREEZE
07 Face Atlasを1枚生成
08 自動抽出
09 FACE-ASSET-FREEZE
10 See-Throughへ
```

まずここまでを実行する。
