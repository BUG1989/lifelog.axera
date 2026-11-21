#!/usr/bin/env python3
"""Check the three AX8860 demo model endpoints."""
from __future__ import annotations

import json
import os
import urllib.request


ENDPOINTS = {
    "qwen3.5-2b": os.environ.get(
        "LIFELOG_REMOTE_QWEN35_2B", "http://127.0.0.1:18086"),
    "minicpm-ocr-1.0": os.environ.get(
        "LIFELOG_REMOTE_MINICPM_OCR", "http://127.0.0.1:18087"),
    "minicpm-v-4.7-35b-a3b": os.environ.get(
        "LIFELOG_REMOTE_MINICPM_V_35B", "http://127.0.0.1:18088"),
}


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode())


def main() -> int:
    ok = True
    for name, base in ENDPOINTS.items():
        try:
            health = get(base.rstrip("/") + "/health")
            models = get(base.rstrip("/") + "/v1/models")
            ids = [item.get("id") for item in models.get("data", [])]
            print(f"{name:30} ok={health.get('status')} model={ids[0] if ids else '?'}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"{name:30} FAILED: {exc}")
    try:
        stats = get(os.environ.get(
            "LIFELOG_STATS_URL", "http://127.0.0.1:8080/api/stats"))
        print("ports:", stats.get("llama", {}).get("listening_ports"))
        print("cmm_gb:", stats.get("cmm", {}).get("used_kb", 0) // 1024 // 1024)
        print("os_avail_gb:", stats.get("mem", {}).get("avail_kb", 0) // 1024 // 1024)
    except Exception as exc:  # noqa: BLE001
        print("tempmon unavailable:", exc)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
