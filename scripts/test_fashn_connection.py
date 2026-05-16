#!/usr/bin/env python3
"""Verify FASHN_API_KEY (auth only — does not run a full try-on)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fitentropy import config  # noqa: E402
from fitentropy.fashn_client import fashn_configured  # noqa: E402


def main() -> int:
    env_path = ROOT / ".env"
    print(f"Reading: {env_path}")
    if not fashn_configured():
        print("FASHN_API_KEY: ✗ empty", file=sys.stderr)
        print(
            "  在 .env 同一行填写： FASHN_API_KEY=你的密钥\n"
            "  保存后执行： grep '^FASHN_API_KEY=.' .env | wc -c  （应 > 20）",
            file=sys.stderr,
        )
        return 1

    print(f"FASHN_API_KEY: ✓ set (len={len(config.FASHN_API_KEY)})")
    url = f"{config.FASHN_API_BASE}/v1/run"
    headers = {
        "Authorization": f"Bearer {config.FASHN_API_KEY}",
        "Content-Type": "application/json",
    }
    # 最小请求：仅验证鉴权（可能返回 4xx 参数错误，但不应是 401）
    resp = requests.post(
        url,
        headers=headers,
        json={"model_name": "tryon-v1.6", "inputs": {}},
        timeout=30,
    )
    if resp.status_code == 401:
        print("FAIL: 401 Unauthorized — Key 无效或已过期", file=sys.stderr)
        return 2
    if resp.status_code in (200, 201, 400, 422):
        print(f"OK: HTTP {resp.status_code} — Key 已被 API 接受")
        try:
            body = resp.json()
            if body.get("id"):
                print(f"  (test prediction id: {body['id'][:24]}…)")
        except json.JSONDecodeError:
            pass
        return 0

    print(f"Unexpected HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
