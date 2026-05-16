"""Heuristic product extraction from retailer HTML (JSON-LD + anchors)."""

from __future__ import annotations

import json
import re
from html import unescape
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from fitentropy.models import ProductLink

JSON_LD_BLOCK = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
    re.IGNORECASE,
)
OG_IMAGE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OG_IMAGE_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.IGNORECASE,
)


def _looks_like_image(url: str) -> bool:
    u = url.lower()
    if not u.startswith("http"):
        return False
    if any(ext in u for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return True
    return "image" in u or "/img" in u or "photos" in u


# ── Garment image ranking heuristics ──
# Keywords that suggest a flat-lay / white-bg / product-only image (preferred for try-on)
_FLAT_LAY_KEYWORDS: tuple[str, ...] = (
    "flat", "flatlay", "flat-lay", "laydown", "lay-down",
    "still", "product", "swatch", "fabric", "detail",
    "front", "back", "plain", "white",
    # Zara/H&M/UNIQLO specific
    "1.webp", "1.jpg", "_1_", "-1-",
)
# Keywords that suggest a model-worn / lifestyle image (should be deprioritized)
_MODEL_WORN_KEYWORDS: tuple[str, ...] = (
    "model", "worn", "wearing", "on-model", "onmodel",
    "look", "lifestyle", "outfit", "studio",
    "shot", "campaign", "lookbook",
    # Common indices for model shots: usually 2nd+ image
    "2.webp", "2.jpg", "_2_", "-2-",
    "3.webp", "3.jpg", "_3_", "-3-",
)


def _is_model_worn_image(url: str) -> bool:
    """True if URL looks like a model-worn / lifestyle image."""
    u = url.lower()
    return any(kw in u for kw in _MODEL_WORN_KEYWORDS)


def _is_flat_lay_image(url: str) -> bool:
    """True if URL looks like a flat-lay / product-only / white-bg image."""
    u = url.lower()
    return any(kw in u for kw in _FLAT_LAY_KEYWORDS)


def _image_tryon_score(url: str) -> int:
    """Score for FASHN try-on suitability. Higher = better.
    - Flat-lay / product-only / white-bg:  +10
    - Model-worn / lifestyle:              -10
    - First image in sequence (1.jpg):      +5
    """
    score = 0
    u = url.lower()
    if _is_flat_lay_image(url):
        score += 10
    if _is_model_worn_image(url):
        score -= 10
    # Prefer the first image (often the product-only shot)
    if re.search(r'[/_-]1[._](webp|jpg|jpeg|png)', u):
        score += 5
    return score


def _collect_all_images(obj: object) -> List[str]:
    """Recursively collect ALL image URLs from a JSON-LD node."""
    results: List[str] = []
    if isinstance(obj, str) and _looks_like_image(obj):
        results.append(obj)
    elif isinstance(obj, dict):
        for k in ("image", "thumbnailUrl", "contentUrl"):
            if k in obj:
                results.extend(_collect_all_images(obj[k]))
        for v in obj.values():
            results.extend(_collect_all_images(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_collect_all_images(item))
    return results


def best_garment_image(urls: List[str]) -> Optional[str]:
    """Pick the best image for FASHN try-on from a list of URLs.
    Prefers flat-lay / white-bg / product-only images,
    filters out model-worn / lifestyle images.
    """
    if not urls:
        return None
    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for u in urls:
        u_stripped = u.strip()
        if u_stripped and u_stripped not in seen:
            seen.add(u_stripped)
            unique.append(u_stripped)
    if not unique:
        return None
    # Score and sort: best try-on image first
    scored = sorted(unique, key=_image_tryon_score, reverse=True)
    return scored[0]


def _first_url(obj: object) -> Optional[str]:
    if isinstance(obj, str) and obj.startswith("http"):
        return obj
    if isinstance(obj, dict):
        for k in ("url", "@id"):
            v = obj.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
        for v in obj.values():
            u = _first_url(v)
            if u:
                return u
    if isinstance(obj, list):
        for item in obj:
            u = _first_url(item)
            if u:
                return u
    return None


def _first_image(obj: object) -> Optional[str]:
    if isinstance(obj, str) and _looks_like_image(obj):
        return obj
    if isinstance(obj, dict):
        for k in ("image", "thumbnailUrl", "contentUrl"):
            if k in obj:
                img = _first_image(obj[k])
                if img:
                    return img
        for v in obj.values():
            img = _first_image(v)
            if img:
                return img
    if isinstance(obj, list):
        for item in obj:
            img = _first_image(item)
            if img:
                return img
    return None


def _og_image(html: str) -> Optional[str]:
    for pat in (OG_IMAGE, OG_IMAGE_ALT):
        m = pat.search(html)
        if m:
            url = unescape(m.group(1).strip())
            if _looks_like_image(url):
                return url
    return None


OG_TITLE = re.compile(
    r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OG_TITLE_ALT = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
    re.IGNORECASE,
)


def _og_title(html: str) -> Optional[str]:
    """Extract og:title from HTML meta tags."""
    for pat in (OG_TITLE, OG_TITLE_ALT):
        m = pat.search(html)
        if m:
            title = unescape(m.group(1).strip())
            if len(title) >= 3:
                return title
    # Also try <title> tag as last resort
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
    if m:
        title = unescape(m.group(1).strip())
        # Clean up: remove site suffix like " | H&M US" or " | ZARA"
        for sep in (" | ", " - ", " — "):
            if sep in title:
                title = title.split(sep)[0].strip()
        if len(title) >= 3:
            return title
    return None


# Price patterns in HTML (common retail formats)
_PRICE_PATTERNS = (
    re.compile(r'["\']price["\']\s*:\s*["\']?([\d.,]+)["\']?', re.I),
    re.compile(r'["\']price["\'][^}]*?["\']value["\']\s*:\s*["\']?([\d.,]+)', re.I),
    re.compile(r'class=["\'][^"\']*price[^"\']*["\'][^>]*>[^<]*?([\$€£¥][\d.,]+)', re.I),
    re.compile(r'["\']priceCurrency["\']\s*:\s*["\']([A-Z]{3})["\'].*?["\']price["\']\s*:\s*["\']?([\d.,]+)', re.I),
)


def _price_from_html(html: str) -> str:
    """Try to extract a price from raw HTML content."""
    for pat in _PRICE_PATTERNS:
        m = pat.search(html)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                return f"{groups[0]} {groups[1]}"
            return groups[0]
    return ""


def _price_display(obj: dict) -> str:
    offers = obj.get("offers")
    if isinstance(offers, dict):
        price = offers.get("price")
        cur = offers.get("priceCurrency") or ""
        if price is not None:
            return f"{cur} {price}".strip()
    if isinstance(offers, list) and offers:
        return _price_display({**obj, "offers": offers[0]})
    return ""


def products_from_json_ld(html: str, base_url: str) -> List[ProductLink]:
    host = urlparse(base_url).netloc
    brand_guess = (
        "Zara"
        if "zara" in host
        else "H&M"
        if "hm.com" in host
        else "UNIQLO"
        if "uniqlo" in host
        else "Shop"
    )
    out: List[ProductLink] = []
    for m in JSON_LD_BLOCK.finditer(html):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        candidates = data if isinstance(data, list) else [data]

        for node in candidates:
            if not isinstance(node, dict):
                continue
            types = node.get("@type")
            tlist = types if isinstance(types, list) else [types] if types else []
            if "Product" not in {str(x) for x in tlist}:
                continue
            name = node.get("name")
            if not isinstance(name, str) or len(name) < 3:
                continue
            url = _first_url(node.get("url")) or _first_url(node) or ""
            # Fix: schema.org is NOT a valid product URL — use base_url instead
            if not url.startswith("http") or "schema.org" in url:
                url = base_url
            # Collect ALL images and pick the best flat-lay for try-on
            all_imgs = _collect_all_images(node)
            best_img = best_garment_image(all_imgs)
            image_url = best_img or _first_image(node) or ""
            price = _price_display(node)
            out.append(
                ProductLink(
                    brand=brand_guess,
                    name=unescape(name)[:180],
                    price_display=price,
                    url=urljoin(base_url, url) if url.startswith("/") else url,
                    image_url=image_url,
                )
            )
            if len(out) >= 8:
                return out
    return out


def first_product_for_query(
    html: str,
    *,
    brand: str,
    search_url: str,
) -> ProductLink:
    items = products_from_json_ld(html, search_url)
    if items:
        first = items[0]
        return ProductLink(
            brand=brand,
            name=first.name,
            price_display=first.price_display,
            url=first.url or search_url,
            image_url=first.image_url,
        )

    # Fallback 1: OG meta tags (works for SPA pages like H&M)
    og_name = _og_title(html)
    og_img = _og_image(html) or ""
    og_price = _price_from_html(html)
    if og_name:
        return ProductLink(
            brand=brand,
            name=og_name,
            price_display=og_price,
            url=search_url,
            image_url=og_img,
        )

    # Fallback 2: prominent product link
    link = re.search(r'href=["\']([^"\']+/product[^"\']+)["\']', html, re.I)
    image_url = og_img
    if link:
        href = unescape(link.group(1))
        return ProductLink(
            brand=brand,
            name=f"{brand} search match",
            price_display="",
            url=href if href.startswith("http") else urljoin(search_url, href),
            image_url=image_url,
        )

    return ProductLink(
        brand=brand,
        name=f"{brand} — open search results",
        price_display="",
        url=search_url,
        image_url=image_url,
    )
