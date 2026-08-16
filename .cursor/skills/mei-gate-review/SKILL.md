---
name: mei-gate-review
description: >-
  Re-evaluate a Mei pipeline gate against v003 specs, artifacts, tests, and
  budget. Use after run_tests.py, when writing 07_reviews/reports, or when
  deciding PASS RETRY ROLLBACK STOP.
---

# mei-gate-review

実装の一部。後付けチェックリストではない。テスト失敗を PASS にしない。前回 PASS を流用しない。直したら同じテスト ID を全部やり直す。

## 手順

1. `07_reviews/gates.yaml` で Gate の成果物・テスト ID・仕様節・rollback を読む
2. `python scripts/run_tests.py --gate <GATE>`。失敗なら decision は PASS にしない
3. 該当 v003 節と成果物を突合する。`spec_drift` にブラウザ Colab や Drive 依存を書く
4. `scripts/review_gate.py` の schema で `review_*.json` を書く
5. `human_approved` は人間が付ける。エージェントは false のまま

## JSON

必須フィールドは schema `07_reviews/schema/gate_review.schema.json`。

`decision` は `PASS` / `RETRY` / `ROLLBACK` / `STOP` のみ。

- RETRY: 同 Gate の局所修正
- ROLLBACK: `rollback_to` 必須
- STOP: cap 超過または Master identity 崩壊。全文生図しない

## 禁止

- テスト skip/fail を pass と書かない
- 成果物欠落を「後で」で PASS しない
- 予算超過を無視しない
