"""FASHN Virtual Try-On API (tryon-v1.6). See https://docs.fashn.ai/api-reference/tryon-v1-6"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

import requests

from fitentropy import config

logger = logging.getLogger(__name__)


def fashn_configured() -> bool:
    return bool(config.FASHN_API_KEY)


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {config.FASHN_API_KEY}",
        "Content-Type": "application/json",
    }


def submit_tryon_v16(
    model_image: str,
    garment_image: str,
    *,
    category: str = "auto",
    mode: str = "balanced",
    garment_photo_type: str = "auto",
    segmentation_free: bool = True,
    moderation_level: str = "permissive",
    output_format: str = "jpeg",
    return_base64: bool = False,
    seed: int | None = None,
    num_samples: int = 1,
) -> str:
    if not fashn_configured():
        raise RuntimeError("FASHN_API_KEY is not configured; virtual try-on is unavailable.")

    inputs: Dict[str, Any] = {
        "model_image": model_image,
        "garment_image": garment_image,
        "category": category,
        "mode": mode,
        "garment_photo_type": garment_photo_type,
        "segmentation_free": segmentation_free,
        "moderation_level": moderation_level,
        "output_format": output_format,
        "return_base64": return_base64,
        "num_samples": max(1, min(4, int(num_samples))),
    }
    if seed is not None:
        inputs["seed"] = int(seed)

    url = f"{config.FASHN_API_BASE}/v1/run"
    body = {"model_name": "tryon-v1.6", "inputs": inputs}
    resp = requests.post(url, headers=_headers(), json=body, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"FASHN /v1/run HTTP {resp.status_code}: {resp.text[:800]}")

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"FASHN unexpected response: {data!r}")
    err = data.get("error")
    if err:
        raise RuntimeError(f"FASHN error: {err}")
    pid = data.get("id")
    if not pid:
        raise RuntimeError(f"FASHN missing prediction id: {data!r}")
    return str(pid)


def submit_tryon_max(
    model_image: str,
    product_image: str,
    *,
    prompt: str = "",
    resolution: str = "1k",
    generation_mode: str = "balanced",
    output_format: str = "jpeg",
    return_base64: bool = False,
    seed: int | None = None,
    num_images: int = 1,
) -> str:
    """Submit Try-On Max request — supports shoes, hats, jewelry, bags."""
    if not fashn_configured():
        raise RuntimeError("FASHN_API_KEY is not configured; virtual try-on is unavailable.")

    inputs: Dict[str, Any] = {
        "model_image": model_image,
        "product_image": product_image,
        "prompt": prompt,
        "resolution": resolution,
        "generation_mode": generation_mode,
        "output_format": output_format,
        "return_base64": return_base64,
        "num_images": max(1, min(4, int(num_images))),
    }
    if seed is not None:
        inputs["seed"] = int(seed)

    url = f"{config.FASHN_API_BASE}/v1/run"
    body = {"model_name": "tryon-max", "inputs": inputs}
    resp = requests.post(url, headers=_headers(), json=body, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"FASHN tryon-max /v1/run HTTP {resp.status_code}: {resp.text[:800]}")

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"FASHN unexpected response: {data!r}")
    err = data.get("error")
    if err:
        raise RuntimeError(f"FASHN tryon-max error: {err}")
    pid = data.get("id")
    if not pid:
        raise RuntimeError(f"FASHN missing prediction id: {data!r}")
    return str(pid)


def run_tryon_max(
    model_image: str,
    product_image: str,
    *,
    poll_interval: float = 3.0,
    timeout: float = 180.0,
    **submit_kw: Any,
) -> List[str]:
    """Submit tryon-max and poll until completed; returns output image URL(s)."""

    pid = submit_tryon_max(model_image, product_image, **submit_kw)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = fetch_status(pid)
        status = data.get("status")
        if status == "completed":
            out = data.get("output") or []
            if not isinstance(out, list):
                return []
            return [str(x) for x in out if x]
        if status == "failed":
            err = data.get("error")
            if isinstance(err, dict):
                name = err.get("name", "FashnError")
                msg = err.get("message", str(err))
                raise RuntimeError(f"{name}: {msg}")
            raise RuntimeError(f"FASHN tryon-max failed: {err!r}")
        time.sleep(poll_interval)

    raise TimeoutError(f"FASHN tryon-max timed out after {timeout:.0f}s (id={pid})")


def fetch_status(prediction_id: str) -> Dict[str, Any]:
    url = f"{config.FASHN_API_BASE}/v1/status/{prediction_id}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"FASHN /v1/status HTTP {resp.status_code}: {resp.text[:800]}")
    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"FASHN status unexpected: {data!r}")
    return data


def run_tryon_v16(
    model_image: str,
    garment_image: str,
    *,
    poll_interval: float = 1.5,
    timeout: float = 120.0,
    **submit_kw: Any,
) -> List[str]:
    """Submit try-on-v1.6 and poll until completed; returns output image URL(s) or base64 strings."""

    pid = submit_tryon_v16(model_image, garment_image, **submit_kw)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = fetch_status(pid)
        status = data.get("status")
        if status == "completed":
            out = data.get("output") or []
            if not isinstance(out, list):
                return []
            return [str(x) for x in out if x]
        if status == "failed":
            err = data.get("error")
            if isinstance(err, dict):
                name = err.get("name", "FashnError")
                msg = err.get("message", str(err))
                raise RuntimeError(f"{name}: {msg}")
            raise RuntimeError(f"FASHN failed: {err!r}")
        time.sleep(poll_interval)

    raise TimeoutError(f"FASHN try-on timed out after {timeout:.0f}s (id={pid})")


def submit_model_create(
    prompt: str,
    *,
    aspect_ratio: str = "3:4",
    generation_mode: str = "balanced",
    resolution: str = "1k",
    output_format: str = "jpeg",
    return_base64: bool = False,
    seed: int | None = None,
    num_images: int = 1,
) -> str:
    if not fashn_configured():
        raise RuntimeError("FASHN_API_KEY is not configured; model-create is unavailable.")

    inputs: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "generation_mode": generation_mode,
        "resolution": resolution,
        "output_format": output_format,
        "return_base64": return_base64,
        "num_images": max(1, min(4, int(num_images))),
    }
    if seed is not None:
        inputs["seed"] = int(seed)

    url = f"{config.FASHN_API_BASE}/v1/run"
    body = {"model_name": "model-create", "inputs": inputs}
    resp = requests.post(url, headers=_headers(), json=body, timeout=60)
    if resp.status_code >= 400:
        raise RuntimeError(f"FASHN model-create HTTP {resp.status_code}: {resp.text[:800]}")

    data = resp.json()
    if not isinstance(data, dict):
        raise RuntimeError(f"FASHN unexpected response: {data!r}")
    err = data.get("error")
    if err:
        raise RuntimeError(f"FASHN error: {err}")
    pid = data.get("id")
    if not pid:
        raise RuntimeError(f"FASHN missing prediction id: {data!r}")
    return str(pid)


def run_model_create(
    prompt: str,
    *,
    poll_interval: float = 2.0,
    timeout: float = 180.0,
    **submit_kw: Any,
) -> List[str]:
    """Poll model-create until completed; returns output URL(s) or base64 strings."""

    pid = submit_model_create(prompt, **submit_kw)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data = fetch_status(pid)
        status = data.get("status")
        if status == "completed":
            out = data.get("output") or []
            if not isinstance(out, list):
                return []
            return [str(x) for x in out if x]
        if status == "failed":
            err = data.get("error")
            if isinstance(err, dict):
                name = err.get("name", "FashnError")
                msg = err.get("message", str(err))
                raise RuntimeError(f"{name}: {msg}")
            raise RuntimeError(f"FASHN model-create failed: {err!r}")
        time.sleep(poll_interval)

    raise TimeoutError(f"FASHN model-create timed out after {timeout:.0f}s (id={pid})")
