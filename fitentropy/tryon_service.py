"""Auto FASHN try-on using garment images from Bright Data retail scrapes."""

from __future__ import annotations

import base64
import logging
import re
from typing import Any, Dict, List

import requests

from fitentropy import config
from fitentropy.brightdata_client import scrape_html
from fitentropy.fashn_client import fashn_configured, run_tryon_v16, run_tryon_max
from fitentropy.mannequin_assets import model_image_for_tryon
from fitentropy.models import ProductLink
from fitentropy.retail_parser import best_garment_image, first_product_for_query

logger = logging.getLogger(__name__)

DEFAULT_PRODUCT_URL = (
    "https://www.zara.com/us/en/adjustable-waist-cropped-trench-coat-p06318049.html"
    "?v1=529348923"
)

# Without Bright Data: Zara pages are mostly SPA, use known product metadata + accessible flat-lay images
_FALLBACK_BY_PRODUCT_ID: Dict[str, dict[str, str]] = {
    "6318049": {
        "brand": "Zara",
        "name": "ADJUSTABLE WAIST CROPPED TRENCH COAT",
        "price_display": "$ 99.90",
        "url": DEFAULT_PRODUCT_URL,
        "image_url": (
            "https://images.unsplash.com/photo-1591047139829-d91aecb6caea"
            "?auto=format&w=900&q=85&fit=crop"
        ),
    },
}


def _product_from_offer(off: dict) -> dict:
    if not isinstance(off, dict):
        return {}
    prod = off.get("product")
    return prod if isinstance(prod, dict) else {}


def resolve_garment_image_url(prod: dict) -> str:
    """Best-effort garment_image for FASHN from scraped product metadata.
    Prefers flat-lay / white-bg / product-only images over model-worn shots.
    """

    image_url = (prod.get("image_url") or "").strip()
    if image_url.startswith("http"):
        # If we already have an image, check if it's model-worn and try to find a better one
        if not _is_model_worn_url(image_url):
            return image_url

    page_url = (prod.get("url") or "").strip()
    if not page_url.startswith("http") or not config.brightdata_configured():
        # Return what we have even if it's model-worn
        return image_url

    try:
        page_html = scrape_html(page_url)
        brand = str(prod.get("brand") or "Shop")
        refreshed = first_product_for_query(page_html, brand=brand, search_url=page_url)
        # first_product_for_query already uses best_garment_image internally
        best = (refreshed.image_url or "").strip()
        if best.startswith("http"):
            return best
        return image_url
    except Exception as exc:
        logger.debug("Garment image scrape failed for %s: %s", page_url, exc)
        return image_url


def _is_model_worn_url(url: str) -> bool:
    """Quick check if URL looks like a model-worn image."""
    u = url.lower()
    return any(kw in u for kw in (
        "model", "worn", "wearing", "on-model", "onmodel",
        "lifestyle", "look", "lookbook", "campaign",
    ))


def garment_image_for_outfit(outfit: dict) -> str:
    """Pick first missing-item product image from outfit offers."""

    for off in outfit.get("offers") or []:
        prod = _product_from_offer(off)
        url = resolve_garment_image_url(prod)
        if url:
            return url
    return ""


# ── Category inference for FASHN API ──
_TOPS_KEYWORDS = (
    "Tops", "shirt", "t-shirt", "hoodie", "knitwear", "blazer", "outerwear", "jacket",
    "coat", "trench", "hoodie", "sweater", "top", "shirt", "jacket",
    "coat", "blazer", "hoodie", "sweater", "cardigan",
)
_BOTTOMS_KEYWORDS = (
    "Bottoms", "pant", "jean", "trouser", "skirt", "short",
    "bottom", "pant", "jean", "trouser", "skirt", "short",
)
_DRESS_KEYWORDS = (
    "Dresses", "dress", "gown",
)


def _infer_fashn_category(label: str) -> str:
    """Map a Chinese missing-label to FASHN category: tops / bottoms / one-pieces."""
    low = label.lower()
    if any(kw in low for kw in _DRESS_KEYWORDS):
        return "one-pieces"
    if any(kw in low for kw in _BOTTOMS_KEYWORDS):
        return "bottoms"
    # Default to tops (covers 上衣, 外套, 衬衫, etc.)
    return "tops"


# Categories FASHN can try on (in priority order)
_TRYON_CATEGORIES = ("tops", "bottoms", "one-pieces")
# Keywords that map to each tryon category
_TRYON_PRIORITY_LABELS = (
    "Tops", "shirt", "t-shirt", "hoodie", "knitwear", "blazer", "outerwear", "jacket",
    "coat", "trench", "hoodie", "sweater", "Bottoms", "pant", "jean", "trouser",
    "skirt", "short", "Dresses", "dress",
)


def _first_tryon_garment(outfit: dict) -> tuple[str, str, str]:
    """Find the best garment for FASHN try-on from an outfit.

    Priority: tops > bottoms > dress (FASHN can't do shoes/accessories).
    Returns (garment_image_url, fashn_category, label).
    """
    offers = outfit.get("offers") or []
    missing = outfit.get("missing_labels") or []

    # Priority 1: find an offer for a tryon-able category (tops/bottoms/dress)
    for off in offers:
        if not isinstance(off, dict):
            continue
        label = str(off.get("label") or "")
        category = _infer_fashn_category(label)
        if category not in _TRYON_CATEGORIES:
            continue  # Skip shoes, accessories
        prod = _product_from_offer(off)
        url = resolve_garment_image_url(prod)
        if url:
            return url, category, label

    # Priority 2: search missing_labels for a tryon-able item
    # Even without an offer, we can try to scrape by label
    for label in missing:
        label_str = str(label).strip()
        category = _infer_fashn_category(label_str)
        if category not in _TRYON_CATEGORIES:
            continue
        # Try to find a product image by scraping
        garment_url = _scrape_garment_by_label(label_str)
        if garment_url:
            return garment_url, category, label_str

    # Priority 3: fallback to first offer even if it's not ideal
    for off in offers:
        if not isinstance(off, dict):
            continue
        label = str(off.get("label") or "")
        prod = _product_from_offer(off)
        url = resolve_garment_image_url(prod)
        if url:
            return url, _infer_fashn_category(label), label

    return "", "tops", ""


def _scrape_garment_by_label(label: str) -> str:
    """Try to find a product image for a label by scraping retail search."""
    if not config.brightdata_configured():
        return ""
    from fitentropy.pipeline import _pick_brand, _search_url
    brand = _pick_brand(label)
    url = _search_url(brand, label)
    try:
        page_html = scrape_html(url)
        product = first_product_for_query(page_html, brand=brand, search_url=url)
        if (product.image_url or "").startswith("http"):
            return product.image_url
        # Try product detail page if available
        if product.url and config.brightdata_configured():
            try:
                detail_html = scrape_html(product.url)
                detail = first_product_for_query(detail_html, brand=brand, search_url=product.url)
                if (detail.image_url or "").startswith("http"):
                    return detail.image_url
            except Exception:
                pass
    except Exception as exc:
        logger.debug("Scrape by label failed for %s: %s", label, exc)
    return ""


def _garment_to_data_uri(url: str) -> str:
    """Download a garment image URL and convert to base64 data-uri.
    FASHN cannot load images from most CDN URLs directly,
    so we download and pass as data-uri instead.
    """
    if url.startswith("data:"):
        return url  # Already a data-uri
    try:
        resp = requests.get(
            url, timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        })
        if resp.status_code == 200 and len(resp.content) > 500:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            # Normalize content type
            if ";" in content_type:
                content_type = content_type.split(";")[0].strip()
            if content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
                content_type = "image/jpeg"
            b64 = base64.b64encode(resp.content).decode()
            return f"data:{content_type};base64,{b64}"
    except Exception as exc:
        logger.debug("Failed to download garment image as data-uri: %s", exc)
    # Return original URL as fallback — FASHN might still be able to load it
    return url


def auto_tryon_for_outfits(
    gender: str,
    body_type: str,
    outfits: List[dict],
    *,
    max_looks: int = 3,
    layered: bool = True,
) -> Dict[int, dict]:
    """
    Run FASHN try-on per look using Bright Data–sourced garment images.

    New logic:
    - Each look: find tops AND bottoms if available
    - Layered mode: model + tops → + bottoms → final composite
    - Non-layered: just pick first garment and try on
    - Shoes / accessories: image + buy link only (FASHN doesn't support)

    Returns {outfit_index_1based: {"tryon_url": str, "tryon_step1_url": str|None, ...}}.
    """

    if not fashn_configured():
        return {}

    model_img, _ = model_image_for_tryon(gender, body_type)
    results: Dict[int, dict] = {}
    used_garments: set[str] = set()  # Deduplicate garment images across looks

    for idx, outfit in enumerate(outfits[:max_looks], start=1):
        offers = outfit.get("offers") or []
        missing = outfit.get("missing_labels") or []

        # Collect try-on-able garments by category
        tops_garment = None  # (image_url, label)
        bottoms_garment = None
        onepieces_garment = None
        shoe_info = []  # [{image_url, label, product}] for non-tryon items

        for off in offers:
            if not isinstance(off, dict):
                continue
            label = str(off.get("label") or "")
            category = _infer_fashn_category(label)
            prod = _product_from_offer(off)
            url = resolve_garment_image_url(prod)

            if category == "tops" and not tops_garment and url:
                tops_garment = (url, label)
            elif category == "bottoms" and not bottoms_garment and url:
                bottoms_garment = (url, label)
            elif category == "one-pieces" and not onepieces_garment and url:
                onepieces_garment = (url, label)
            elif category not in _TRYON_CATEGORIES and url:
                shoe_info.append({"image_url": url, "label": label, "product": prod})

        # Determine try-on strategy
        final_tryon_url = None
        step1_url = None
        best_label = ""
        best_category = ""
        garment_url = ""

        try:
            if onepieces_garment:
                # One-piece (dress): single try-on
                g_url, g_label = onepieces_garment
                garment_data_uri = _garment_to_data_uri(g_url)
                urls = run_tryon_v16(
                    model_img, garment_data_uri,
                    category="one-pieces",
                    garment_photo_type="auto",
                    timeout=180.0,
                )
                if urls:
                    final_tryon_url = urls[0]
                    garment_url = g_url
                    best_label = g_label
                    best_category = "one-pieces"

            elif tops_garment and bottoms_garment and layered:
                # Layered: model + tops → + bottoms
                tops_url, tops_label = tops_garment
                bottoms_url, bottoms_label = bottoms_garment

                # Step 1: model + tops
                tops_data_uri = _garment_to_data_uri(tops_url)
                step1_urls = run_tryon_v16(
                    model_img, tops_data_uri,
                    category="tops",
                    garment_photo_type="auto",
                    timeout=180.0,
                )
                if step1_urls:
                    step1_url = step1_urls[0]

                    # Step 2: step1 result + bottoms
                    step1_data_uri = _garment_to_data_uri(step1_url)
                    final_urls = run_tryon_v16(
                        step1_data_uri,
                        _garment_to_data_uri(bottoms_url),
                        category="bottoms",
                        garment_photo_type="auto",
                        timeout=180.0,
                    )
                    if final_urls:
                        final_tryon_url = final_urls[0]
                        garment_url = tops_url
                        best_label = f"{tops_label} + {bottoms_label}"
                        best_category = "tops+bottoms"
                    else:
                        # Step 2 failed, return step 1
                        final_tryon_url = step1_url
                        garment_url = tops_url
                        best_label = tops_label
                        best_category = "tops"
                else:
                    # Step 1 failed, try bottoms alone
                    bottoms_data_uri = _garment_to_data_uri(bottoms_url)
                    fallback_urls = run_tryon_v16(
                        model_img, bottoms_data_uri,
                        category="bottoms",
                        garment_photo_type="auto",
                        timeout=180.0,
                    )
                    if fallback_urls:
                        final_tryon_url = fallback_urls[0]
                        garment_url = bottoms_url
                        best_label = bottoms_label
                        best_category = "bottoms"

            elif tops_garment:
                g_url, g_label = tops_garment
                garment_data_uri = _garment_to_data_uri(g_url)
                urls = run_tryon_v16(
                    model_img, garment_data_uri,
                    category="tops",
                    garment_photo_type="auto",
                    timeout=180.0,
                )
                if urls:
                    final_tryon_url = urls[0]
                    garment_url = g_url
                    best_label = g_label
                    best_category = "tops"

            elif bottoms_garment:
                g_url, g_label = bottoms_garment
                garment_data_uri = _garment_to_data_uri(g_url)
                urls = run_tryon_v16(
                    model_img, garment_data_uri,
                    category="bottoms",
                    garment_photo_type="auto",
                    timeout=180.0,
                )
                if urls:
                    final_tryon_url = urls[0]
                    garment_url = g_url
                    best_label = g_label
                    best_category = "bottoms"

        except Exception as exc:
            logger.warning("FASHN try-on failed for look %s: %s", idx, exc)

        if not final_tryon_url:
            logger.info("No try-on result for look %s", idx)
            continue

        # Dedup
        if garment_url in used_garments:
            logger.info("Duplicate garment for look %s, skipping", idx)
            continue
        used_garments.add(garment_url)

        result = {
            "tryon_url": final_tryon_url,
            "garment_url": garment_url,
            "category": best_category,
            "label": best_label,
        }
        if step1_url:
            result["tryon_step1_url"] = step1_url

        # Shoes try-on via tryon-max (supports shoes, hats, jewelry, bags)
        if shoe_info:
            try:
                for _si, _shoe in enumerate(shoe_info[:1]):  # Try first shoe only
                    _shoe_img_url = _shoe.get("image_url", "")
                    if not _shoe_img_url:
                        continue
                    _shoe_data_uri = _garment_to_data_uri(_shoe_img_url)
                    # Use the clothing try-on result as model for shoes
                    _shoe_model = _garment_to_data_uri(final_tryon_url)
                    _shoe_urls = run_tryon_max(
                        _shoe_model,
                        _shoe_data_uri,
                        prompt="put the shoes on the model",
                        resolution="1k",
                        generation_mode="balanced",
                        timeout=180.0,
                    )
                    if _shoe_urls:
                        result["tryon_shoes_url"] = _shoe_urls[0]
                        best_category = f"{best_category}+shoes"
                        result["category"] = best_category
                        _shoe_label = _shoe.get("label", "")
                        if _shoe_label:
                            best_label = f"{best_label} + {_shoe_label}"
                            result["label"] = best_label
                        # Update final_tryon_url to the shoes-included version
                        final_tryon_url = _shoe_urls[0]
                        result["tryon_url"] = final_tryon_url
                        break
            except Exception as exc:
                logger.warning("FASHN tryon-max (shoes) failed for look %s: %s", idx, exc)
            result["shoes"] = shoe_info

        results[idx] = result

    return results


def _brand_from_url(url: str) -> str:
    u = url.lower()
    if "zara" in u:
        return "Zara"
    if "hm.com" in u or "h&m" in u:
        return "H&M"
    if "uniqlo" in u:
        return "UNIQLO"
    return "Shop"


def _product_id_from_url(product_url: str) -> str:
    m = re.search(r"/p0*(\d+)\.html", product_url, re.I)
    return m.group(1) if m else ""


def _fetch_html_direct(product_url: str) -> str:
    resp = requests.get(
        product_url,
        timeout=60,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    resp.raise_for_status()
    return resp.text


def _fallback_product(product_url: str) -> ProductLink | None:
    pid = _product_id_from_url(product_url)
    meta = _FALLBACK_BY_PRODUCT_ID.get(pid)
    if not meta and pid:
        meta = _FALLBACK_BY_PRODUCT_ID.get(pid.lstrip("0") or pid)
    if not meta and "06318049" in product_url:
        meta = _FALLBACK_BY_PRODUCT_ID.get("6318049")
    if meta:
        return ProductLink(**{**meta, "url": product_url or meta.get("url", "")})
    return None


def product_from_page_url(product_url: str) -> ProductLink:
    """Scrape product page and extract name + garment image."""

    product_url = (product_url or "").strip()
    if not product_url.startswith("http"):
        raise ValueError("Please enter a valid product URL")

    brand = _brand_from_url(product_url)

    if config.brightdata_configured():
        html = scrape_html(product_url)
        prod = first_product_for_query(html, brand=brand, search_url=product_url)
        if (prod.image_url or "").startswith("http"):
            return prod

    try:
        html = _fetch_html_direct(product_url)
        prod = first_product_for_query(html, brand=brand, search_url=product_url)
        if (prod.image_url or "").startswith("http"):
            return prod
        if prod.name and "open search" not in prod.name.lower():
            fb = _fallback_product(product_url)
            if fb:
                return ProductLink(
                    brand=brand,
                    name=prod.name,
                    price_display=prod.price_display,
                    url=product_url,
                    image_url=fb.image_url,
                )
    except Exception as exc:
        logger.debug("Direct fetch failed for %s: %s", product_url, exc)

    fb = _fallback_product(product_url)
    if fb:
        return fb

    raise RuntimeError(
        "Could not extract a usable garment image from the product page. "
        "Please configure BRIGHTDATA_API_KEY, or try again later."
    )


def tryon_product_url(
    gender: str,
    body_type: str,
    product_url: str,
    *,
    category: str = "auto",
) -> dict[str, Any]:
    """
    Scrape Zara/retail URL → FASHN try-on.
    Returns product metadata, garment_image_url, tryon_url.
    """

    if not fashn_configured():
        raise RuntimeError("FASHN not configured, cannot generate try-on image")

    prod = product_from_page_url(product_url)
    prod_dict = prod.model_dump()
    garment = resolve_garment_image_url(prod_dict) or (prod.image_url or "").strip()
    if not garment.startswith("http"):
        raise RuntimeError("Could not extract a usable garment image from the product page")

    model_img, _ = model_image_for_tryon(gender, body_type)
    urls = run_tryon_v16(
        model_img,
        garment,
        category=category,
        garment_photo_type="auto",
        timeout=180.0,
    )
    if not urls:
        raise RuntimeError("Try-on generation failed, please try again later")

    fb = _fallback_product(product_url)
    return {
        "product": prod_dict,
        "garment_image_url": garment,
        "tryon_url": urls[0],
        "product_url": product_url,
        "used_fallback_garment": bool(fb and garment == fb.image_url),
    }
