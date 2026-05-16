"""End-to-end outfit generation (trends → Qwen → retail enrichment)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from urllib.parse import quote_plus

from fitentropy import config
from fitentropy.actionbook_client import collect_retail_manual_hints
from fitentropy.brightdata_client import scrape_html
from fitentropy.evermind_memory import recall_style_context, remember_outfit_turn
from fitentropy.mock_data import mock_pipeline_result, mock_pipeline_male_result
from fitentropy.models import MissingItemOffer, OutfitPlan, PipelineResult, ProductLink
from fitentropy.qwen_client import build_outfit_prompt, chat_completion_json
from fitentropy.retail_parser import first_product_for_query
from fitentropy.trends import fetch_trend_keywords

logger = logging.getLogger(__name__)


def _all_colors_flat(color_by_category: Dict[str, List[str]] | None) -> List[str]:
    if not color_by_category:
        return []
    seen: set[str] = set()
    out: List[str] = []
    for vals in color_by_category.values():
        for c in vals or []:
            if c and c not in seen:
                seen.add(c)
                out.append(c)
    return out


def _pick_brand(seed: str) -> str:
    s = sum(ord(c) for c in seed) % 3
    return ("Zara", "H&M", "UNIQLO")[s]


def _search_url(brand: str, query: str) -> str:
    q = quote_plus(query)
    template = config.RETAIL_SEARCH.get(brand)
    if not template:
        template = config.RETAIL_SEARCH["Zara"]
    return template.format(q=q)


def _enrich_label(label: str, color_terms: List[str] | None = None) -> MissingItemOffer:
    brand = _pick_brand(label)
    extra = " ".join((color_terms or [])[:2])
    query = f"{label} {extra}".strip()
    url = _search_url(brand, query)
    try:
        html = scrape_html(url)
        product = first_product_for_query(html, brand=brand, search_url=url)
        if not product.image_url and product.url and config.brightdata_configured():
            try:
                detail_html = scrape_html(product.url)
                detail = first_product_for_query(
                    detail_html, brand=brand, search_url=product.url
                )
                if detail.image_url:
                    product = ProductLink(
                        brand=brand,
                        name=detail.name or product.name,
                        price_display=detail.price_display or product.price_display,
                        url=detail.url or product.url,
                        image_url=detail.image_url,
                    )
            except Exception as exc:
                logger.debug("Product detail scrape failed for %s: %s", product.url, exc)
    except Exception as exc:
        logger.debug("Retail scrape failed for %s: %s", url, exc)
        product = ProductLink(
            brand=brand,
            name=f"{brand} — {label}",
            price_display="",
            url=url,
            image_url="",
        )
    return MissingItemOffer(label=label, product=product)


def _parse_outfits(raw: Dict[str, Any]) -> List[OutfitPlan]:
    outfits_raw = raw.get("outfits")
    if not isinstance(outfits_raw, list):
        return []

    outfits: List[OutfitPlan] = []
    for row in outfits_raw[:3]:
        if not isinstance(row, dict):
            continue
        missing = row.get("missing_labels") or []
        if not isinstance(missing, list):
            missing = []
        missing_strs = [str(x).strip() for x in missing if str(x).strip()]
        outfits.append(
            OutfitPlan(
                title=str(row.get("title") or "Outfit").strip(),
                description=str(row.get("description") or "").strip(),
                trend_rationale=str(row.get("trend_rationale") or "").strip(),
                missing_labels=missing_strs,
                offers=[],
            )
        )
    return outfits


def run_pipeline(
    *,
    demo_mode: bool,
    user_id: str,
    gender: str,
    occasion: str,
    owned_items: List[str],
    budget_tier: str,
    color_by_category: Dict[str, List[str]] | None = None,
    body_profile: Dict[str, Any] | None = None,
    style_preferences: List[str] | None = None,
) -> PipelineResult:
    if demo_mode:
        if gender == "男":
            return mock_pipeline_male_result()
        return mock_pipeline_result()

    color_by_category = color_by_category or {}
    color_terms_flat = _all_colors_flat(color_by_category)
    memory_snippet = recall_style_context(user_id) if user_id else ""
    actionbook_hints = collect_retail_manual_hints()

    trends = fetch_trend_keywords()
    bd_note = ""
    if not config.brightdata_configured():
        bd_note = "未配置 Bright Data：趋势与商品链接使用内置关键词与搜索直达（无实时爬取）。"
    messages = build_outfit_prompt(
        gender=gender,
        occasion=occasion,
        owned_items=owned_items,
        budget_tier=budget_tier,
        trend_keywords=trends,
        memory_context=memory_snippet,
        actionbook_hints=actionbook_hints or None,
        color_by_category=color_by_category or None,
        body_profile=body_profile or None,
        style_preferences=style_preferences or None,
    )
    raw = chat_completion_json(messages)
    outfits = _parse_outfits(raw)

    if len(outfits) < 3:
        return PipelineResult(
            trend_keywords=trends,
            outfits=outfits,
            demo_mode=False,
            notes="模型返回的搭配不足 3 套，请重试或检查 LLM / 模型名配置。",
            memory_snippet=memory_snippet,
            actionbook_hints=actionbook_hints,
        )

    for outfit in outfits:
        offers: List[MissingItemOffer] = []
        for label in outfit.missing_labels[:5]:
            offers.append(_enrich_label(label, color_terms_flat))
        outfit.offers = offers

    remember_outfit_turn(
        user_id,
        gender=gender,
        occasion=occasion,
        owned_items=owned_items,
        budget_tier=budget_tier,
        trend_keywords=trends,
        outfit_titles=[o.title for o in outfits],
        color_by_category=color_by_category,
        body_profile=body_profile,
        style_preferences=style_preferences,
    )

    return PipelineResult(
        trend_keywords=trends,
        outfits=outfits,
        demo_mode=False,
        notes=bd_note,
        memory_snippet=memory_snippet,
        actionbook_hints=actionbook_hints,
    )
