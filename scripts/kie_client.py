"""KIE.ai client. One module for credit / upload / create / poll / download.

Do not write one-off SDK runners. Call this from generate/edit scripts.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

from scripts.repo import ROOT

API_BASE = "https://api.kie.ai"
UPLOAD_BASE = "https://kieai.redpandaai.co"
POLL_TIMEOUT_S = 15 * 60
POLL_INTERVALS = (3, 5, 8, 13, 21, 30)


class KieError(RuntimeError):
    pass


def load_api_key() -> str:
    load_dotenv(ROOT / ".env")
    key = os.environ.get("KIE_API_KEY") or os.environ.get("KITAI_API_KEY") or ""
    if not key.strip():
        raise KieError("KIE_API_KEY is missing. Copy .env.example to .env.")
    return key.strip()


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def get_credits(client: httpx.Client | None = None) -> int:
    api_key = load_api_key()
    own = client is None
    http = client or httpx.Client(timeout=30.0)
    try:
        response = http.get(f"{API_BASE}/api/v1/chat/credit", headers=_headers(api_key))
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") not in (200, "200", None) and "data" not in payload:
            raise KieError(f"credit check failed: {payload}")
        data = payload.get("data", payload)
        if isinstance(data, dict):
            return int(data.get("credit") or data.get("credits") or data.get("balance") or 0)
        return int(data)
    finally:
        if own:
            http.close()


def upload_file(path: Path, upload_path: str = "mei") -> str:
    api_key = load_api_key()
    with path.open("rb") as handle:
        files = {"file": (path.name, handle, "application/octet-stream")}
        data = {"uploadPath": upload_path, "fileName": path.name}
        with httpx.Client(timeout=120.0) as http:
            response = http.post(
                f"{UPLOAD_BASE}/api/file-stream-upload",
                headers=_headers(api_key),
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()
    data_obj = payload.get("data") or payload
    url = data_obj.get("fileUrl") or data_obj.get("downloadUrl")
    if not url:
        raise KieError(f"upload returned no URL: {payload}")
    return url


def create_task(model: str, input_payload: dict) -> str:
    api_key = load_api_key()
    body = {"model": model, "input": input_payload}
    with httpx.Client(timeout=60.0) as http:
        response = http.post(
            f"{API_BASE}/api/v1/jobs/createTask",
            headers={**_headers(api_key), "Content-Type": "application/json"},
            json=body,
        )
        response.raise_for_status()
        payload = response.json()
    data = payload.get("data") or payload
    task_id = data.get("taskId") or data.get("task_id")
    if not task_id:
        raise KieError(f"createTask returned no taskId: {payload}")
    return str(task_id)


def poll_task(task_id: str, timeout_s: int = POLL_TIMEOUT_S) -> dict:
    api_key = load_api_key()
    deadline = time.time() + timeout_s
    interval_index = 0
    with httpx.Client(timeout=30.0) as http:
        while time.time() < deadline:
            response = http.get(
                f"{API_BASE}/api/v1/jobs/recordInfo",
                headers=_headers(api_key),
                params={"taskId": task_id},
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data") or payload
            state = str(data.get("state") or data.get("status") or "").lower()
            if state in {"success", "succeed", "completed", "done"}:
                return data
            if state in {"fail", "failed", "error"}:
                raise KieError(f"task failed: {data}")
            sleep_for = POLL_INTERVALS[min(interval_index, len(POLL_INTERVALS) - 1)]
            interval_index += 1
            time.sleep(sleep_for)
    raise KieError(f"task {task_id} timed out after {timeout_s}s")


def download_result(file_url: str, dest: Path) -> Path:
    api_key = load_api_key()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120.0, follow_redirects=True) as http:
        resolved = file_url
        try:
            response = http.post(
                f"{API_BASE}/api/v1/common/download-url",
                headers={**_headers(api_key), "Content-Type": "application/json"},
                json={"url": file_url},
            )
            if response.is_success:
                payload = response.json()
                data = payload.get("data") or payload
                if isinstance(data, str) and data.startswith("http"):
                    resolved = data
                elif isinstance(data, dict):
                    resolved = data.get("url") or data.get("downloadUrl") or resolved
        except httpx.HTTPError:
            resolved = file_url
        download = http.get(resolved)
        download.raise_for_status()
        dest.write_bytes(download.content)
    return dest


def result_urls(task_data: dict) -> list[str]:
    urls: list[str] = []
    for key in ("resultUrls", "result_urls", "outputUrls"):
        value = task_data.get(key)
        if isinstance(value, list):
            urls.extend(str(item) for item in value)
    result_json = task_data.get("resultJson")
    if isinstance(result_json, str) and result_json.startswith("{"):
        import json

        parsed = json.loads(result_json)
        for key in ("resultUrls", "urls"):
            value = parsed.get(key)
            if isinstance(value, list):
                urls.extend(str(item) for item in value)
    info = task_data.get("info")
    if isinstance(info, dict):
        value = info.get("result_urls") or info.get("resultUrls")
        if isinstance(value, list):
            urls.extend(str(item) for item in value)
    return urls
