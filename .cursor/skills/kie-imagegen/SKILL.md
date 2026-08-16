---
name: kie-imagegen
description: >-
  Generate or edit images through kie.ai (GPT Image 2 i2i and Grok Imagine 2.0).
  Use when creating Mei assets, Face Atlas, local edits, PSD RGB repair, checking
  KIE credits, uploading files, polling jobs, or saving download-url results.
---

# kie-imagegen

OpenAI Images API と `openai` パッケージは使わない。実行は必ず [`scripts/kie_client.py`](scripts/kie_client.py)。ワンオフランナー禁止。

## Auth

- `.env` の `KIE_API_KEY`（ローカル別名 `KITAI_API_KEY` も読む）
- Header: `Authorization: Bearer`
- Jobs: `https://api.kie.ai` `POST /api/v1/jobs/createTask`（HTTP 200 = 作成完了ではない）
- Status: `GET /api/v1/jobs/recordInfo?taskId=`
- Upload: `https://kieai.redpandaai.co` `POST /api/file-stream-upload` → `fileUrl` / `downloadUrl`
- Download: `POST /api/v1/common/download-url` のあと **即ローカル保存**（リンク期限 20 分）
- 生成前に `get_credits()`

## Modes

| mode | model | 用途 |
| --- | --- | --- |
| generate-ref | `gpt-image-2-image-to-image` | Master / Atlas / 局所 overlay |
| generate-t2i | `grok-imagine-image-2-0/text-to-image` | 一般 t2i。**Mei 全身 Master 禁止** |
| edit-gpt | `gpt-image-2-image-to-image` | mask なし。overlay + 「change only X; keep Y」 |
| edit-grok | `grok-imagine-image-2-0/image-edit` | 元画像の `task_id` + `mask_indexs`。PNG URL では呼べない |

Grok segment-map: `grok-imagine-image-2-0/segment-map`。`task_id` は元画像タスク。GPT `task_id` が拒否されたら `grok_edit_unavailable` と log して停止。全文生図しない。

`grok-imagine/image-to-image`（1.x）は使わない。

## Mei 固定

- Master: `aspect_ratio: "2:3"`, `resolution: "1K"`。4K 禁止
- Atlas: 1 枚。G002R は構造失敗時 1 回
- Repair: RGB のみ。alpha はコード
- Brief はキャプションではなく指示。1 edit = 1 region。参照画像の役割を書く

正本: [i2i](https://docs.kie.ai/market/gpt/gpt-image-2-image-to-image), [image-edit](https://docs.kie.ai/market/grok-imagine-image-2-0/image-edit), [segment-map](https://docs.kie.ai/market/grok-imagine-image-2-0/segment-map), [t2i](https://docs.kie.ai/market/grok-imagine-image-2-0/text-to-image), [upload](https://docs.kie.ai/file-upload-api/quickstart), [common](https://docs.kie.ai/common-api/quickstart), [recordInfo](https://docs.kie.ai/market/common/get-task-detail)
