# GPT Image 2 i2i と Grok 2.0

- createTask の 200 はジョブ作成。完了は recordInfo
- poll backoff。timeout 10–15 分。v0.1 は webhook なし
- download-url は 20 分で切れるので即保存
- Grok edit は source task_id。segment-map の task_id ではない
- mask_indexs の min 1 vs segment index 0 は実行時に確認
