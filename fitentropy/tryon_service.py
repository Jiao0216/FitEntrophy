"""Auto FASHN try-on using garment images from Bright Data retail scrapes."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fitentropy import config
from fitentropy.brightdata_client import scrape_html
from fitentropy.fashn_client import fashn_configured, run_tryon_v16
from fitentropy.mannequin_assets import model_image_for_tryon
from fitentropy.retail_parser import first_product_for_query

logger = logging.getLogger(__name__)


def _product_from_offer(off: dict) -> dict:
    if not isinstance(off, dict):
        return {}
    prod = off.get("product")
    return prod if isinstance(prod, dict) else {}


def resolve_garment_image_url(prod: dict) -> str:
    """Best-effort garment_image for FASHN from scraped product metadata."""

    image_url = (prod.get("image_url") or "").strip()
    if image_url.startswith("http"):
        return image_url

    page_url = (prod.get("url") or "").strip()
    if not page_url.startswith("http") or not config.brightdata_configured():
        return ""

    try:
        html = scrape_html(page_url)
        brand = str(prod.get("brand") or "Shop")
        refreshed = first_product_for_query(html, brand=brand, search_url=page_url)
        return (refreshed.image_url or "").strip()
    except Exception as exc:
        logger.debug("Garment image scrape failed for %s: %s", page_url, exc)
        return ""


def garment_image_for_outfit(outfit: dict) -> str:
    """Pick first missing-item product image from outfit offers."""

    for off in outfit.get("offers") or []:
        prod = _product_from_offer(off)
        url = resolve_garment_image_url(prod)
        if url:
            return url
    return ""


def auto_tryon_for_outfits(
    gender: str,
    body_type: str,
    outfits: List[dict],
    *,
    max_looks: int = 3,
) -> Dict[int, str]:
    """
    Run FASHN try-on per look using Bright Data–sourced garment images.
    Returns {outfit_index_1based: output_image_url}.
    """

    if not fashn_configured():
        return {}

    model_img, _ = model_image_for_tryon(gender, body_type)
    results: Dict[int, str] = {}

    for idx, outfit in enumerate(outfits[:max_looks], start=1):
        garment = garment_image_for_outfit(outfit)
        if not garment:
            logger.info("No garment image for look %s, skipping try-on", idx)
            continue
        try:
            urls = run_tryon_v16(model_img, garment, timeout=180.0)
            if urls:
                results[idx] = urls[0]
        except Exception as exc:
            logger.warning("FASHN try-on failed for look %s: %s", idx, exc)

    return results
