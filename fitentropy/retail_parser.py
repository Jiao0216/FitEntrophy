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
            url = _first_url(node.get("url")) or _first_url(node) or base_url
            image_url = _first_image(node.get("image")) or _first_image(node) or ""
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

  # Fallback: prominent product link
    link = re.search(r'href=["\']([^"\']+/product[^"\']+)["\']', html, re.I)
    image_url = _og_image(html) or ""
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
