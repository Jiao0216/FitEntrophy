"""Derive trend keywords from scraped editorial / discovery pages."""

from __future__ import annotations

import logging
import re
from html import unescape
from typing import List, Set

from fitentropy import config
from fitentropy.brightdata_client import scrape_html

logger = logging.getLogger(__name__)

# High-signal seeds if the page is sparse or blocked
FALLBACK_KEYWORDS = [
    "quiet luxury",
    "wide-leg tailoring",
    "capsule layering",
    "metallic evening",
    "ballet flats",
    "denim maxi",
    "sheer overlays",
    "sport-luxe",
    "monochrome base",
    "soft utility",
]

HASHTAG = re.compile(r"#[\w\u00c0-\u024f\u4e00-\u9fff]{2,32}", re.UNICODE)
META_CONTENT = re.compile(
    r'<meta[^>]+(?:name|property)=["\'](?:description|keywords|og:title|og:description)["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def _strip_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text).strip())


def extract_keywords_from_html(html: str, max_terms: int = 12) -> List[str]:
    found: Set[str] = set()

    for m in META_CONTENT.finditer(html):
        blob = unescape(m.group(1))
        for part in re.split(r"[,.;|/]", blob):
            part = part.strip()
            if 3 <= len(part) <= 48:
                found.add(part.lower())

    for tag in HASHTAG.findall(html):
        found.add(tag.lstrip("#").lower())

    lowered = html.lower()
    for seed in FALLBACK_KEYWORDS:
        if seed.lower() in lowered:
            found.add(seed.lower())

    # Title-ish: first clear line in visible text
    visible = _strip_tags(html)[:4000].lower()
    for seed in FALLBACK_KEYWORDS:
        if seed.lower() in visible:
            found.add(seed.lower())

    out = sorted(found, key=len, reverse=True)
    return out[:max_terms] if out else list(FALLBACK_KEYWORDS[:max_terms])


def fetch_trend_keywords() -> List[str]:
    """Scrape configured sources via Bright Data; never raises — degrades to seeds."""

    if not config.brightdata_configured():
        return list(FALLBACK_KEYWORDS[:12])

    aggregated: List[str] = []
    for url in config.TREND_SOURCES:
        try:
            html = scrape_html(url)
        except Exception as exc:
            logger.debug("Trend scrape failed for %s: %s", url, exc)
            continue
        aggregated.extend(extract_keywords_from_html(html))

    # Dedupe preserving order
    seen: Set[str] = set()
    deduped: List[str] = []
    for k in aggregated:
        kl = k.strip().lower()
        if kl and kl not in seen:
            seen.add(kl)
            deduped.append(kl)

    if len(deduped) < 5:
        deduped.extend(FALLBACK_KEYWORDS)
        seen = set()
        out: List[str] = []
        for k in deduped:
            kl = k.strip().lower()
            if kl not in seen:
                seen.add(kl)
                out.append(kl)
        return out[:12]

    return deduped[:12]
