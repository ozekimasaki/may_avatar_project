# MASTER-FREEZE

仕様 §13–20。

- [ ] QA JSON に hard_fail / scores / total / decision
- [ ] hard_fail 0 かつ total >= 90 で FREEZE
- [ ] 80–89 なら GPT overlay 最大 2。Hard なら局所 edit のみ。直らなければ STOP
- [ ] mei_master_v001.png / .sha256 / master_qa_v001.json
- [ ] 候補 PNG は残す
- [ ] freeze 後に FULL 行が増えていない
