"""Bright Data Web Unlocker via REST."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import requests

from fitentropy import config

logger = logging.getLogger(__name__)


class BrightDataError(RuntimeError):
    pass


def scrape_html(url: str, *, zone: Optional[str] = None, timeout: int = 120) -> str:
    """Return raw HTML (or text body) for ``url`` using Bright Data Unlocker."""

    if not config.BRIGHTDATA_API_KEY:
        raise BrightDataError("BRIGHTDATA_API_KEY is not set")

    payload: Dict[str, Any] = {
        "zone": zone or config.BRIGHTDATA_ZONE,
        "url": url,
        "format": "raw",
        "method": "GET",
    }
    headers = {
        "Authorization": f"Bearer {config.BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        config.BRIGHTDATA_REQUEST_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=timeout,
    )
    if resp.status_code >= 400:
        raise BrightDataError(f"Bright Data HTTP {resp.status_code}: {resp.text[:500]}")

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return resp.text

    body = data.get("body")
    if isinstance(body, str):
        return body
    if body is None:
        return resp.text
    return str(body)
