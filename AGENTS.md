# AGENTS.md

メイ配信用アバターの AI-first パイプライン。Python 製の CLI スクリプト群 + pytest。Web サーバや常駐サービスは無い。
正本は [`README.md`](README.md) と `docs/*_v003.md`。Gate 定義は [`07_reviews/gates.yaml`](07_reviews/gates.yaml)。

## Cursor Cloud specific instructions

環境は Python 3.12 の venv (`.venv`) を使う。依存は update script が `.venv` に入れる（`requirements.txt`）。
コマンドを打つ前に `source .venv/bin/activate` するか、`.venv/bin/python` を直接使う。

### スクリプトの実行

`scripts/*.py` の多くは `from scripts.xxx import ...` でパッケージ import する。
リポジトリ root を path に載せるか、モジュールとして実行する:

```bash
python -m scripts.review_gate --validate-schema
python -m scripts.budget --check-header
python -m scripts.inx_inspect
```

`review_gate.py` と `inx_inspect.py` は `python scripts/foo.py` でも repo root を `sys.path` に足す。
CI は job 全体に `PYTHONPATH: ${{ github.workspace }}` を付け、`python -m scripts.*` を使う。

`pytest` は `pytest.ini` に `pythonpath = .` があるので `PYTHONPATH` 無しで通る。

### テスト / 検証 (CI 相当)

```bash
pytest tests/                                    # 55 passed / 12 skipped が正常
python scripts/run_tests.py --gate SPEC-FREEZE
python -m scripts.review_gate --validate-schema
python -m scripts.budget --check-header
```

`require_path` が該当 Gate 以外で skip するテストは、まだ人間作業の成果物が無いため（Session CSV、OBS スクショ、30分録画）。欠陥ではない。

### アプリ実行 (パイプライン本体)

画像・PSD 処理系スクリプトはローカルの `01_art/` 資産に対してオフラインで動く（例: `scripts/qa_master.py` は `avatar_base.png` を解析して `01_art/master/master_qa_v001.json` を出力）。実行すると tracked な成果物 (JSON 等) を上書きすることがあるので、デモ後は `git checkout -- <path>` で戻すこと。

`scripts/kie_client.py` を使う生成/編集系 (`generate_face_atlas.py`, `edit_master.py` 等) は `KIE_API_KEY` が必要。`.env.example` を `.env` にコピーして key を入れる。See-Through (`scripts/st_run_colab.sh`) は GPU/Colab が要るのでこの環境では走らない。

Inochi Creator の GUI（ノード階層、パラメータ、まばたき/口テクスチャ、スクショ）は人間作業。`may.inx` を捏造しない。読み取りは `python -m scripts.inx_inspect`。

### 予算・Gate ルール

画像生成 hard cap は 6、MASTER-FREEZE 後の全身再生成は 0。詳細は `README.md` と `.cursor/skills/mei-master/SKILL.md` を参照。
