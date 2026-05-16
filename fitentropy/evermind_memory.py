"""EverOS (Evermind) — episodic memory for FitEntropy styling context."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List

from fitentropy import config

logger = logging.getLogger(__name__)


def _client():
    if not config.EVEROS_API_KEY:
        return None
    try:
        from everos import EverOS
    except ImportError:
        logger.debug("everos package not installed")
        return None
    return EverOS(api_key=config.EVEROS_API_KEY)


def recall_style_context(user_id: str) -> str:
    """Pull short personalization context for the Qwen prompt."""

    client = _client()
    if not client:
        return ""

    try:
        resp = client.v1.memories.search(
            filters={"user_id": user_id},
            query="FitEntropy wardrobe outfits style budget occasions owned items",
            top_k=6,
            method="hybrid",
            memory_types=["episodic_memory", "profile"],
        )
    except Exception as exc:
        logger.debug("EverOS search failed: %s", exc)
        return ""

    snippets: List[str] = []
    data = resp.data
    if not data:
        return ""

    for ep in data.episodes or []:
        if ep.summary:
            snippets.append(ep.summary.strip())
        elif ep.episode:
            snippets.append(ep.episode.strip()[:400])

    for prof in data.profiles or []:
        if prof.profile_data:
            snippets.append(json.dumps(prof.profile_data, ensure_ascii=False)[:400])

    if not snippets:
        return ""

    return " | ".join(snippets[:4])


def remember_outfit_turn(
    user_id: str,
    *,
    gender: str,
    occasion: str,
    owned_items: List[str],
    budget_tier: str,
    trend_keywords: List[str],
    outfit_titles: List[str],
    color_by_category: Dict[str, List[str]] | None = None,
    body_profile: Dict[str, Any] | None = None,
    style_preferences: List[str] | None = None,
) -> None:
    """Append a compact user message so EverOS can extract episodic memory."""

    client = _client()
    if not client:
        return

    payload = {
        "app": "FitEntropy",
        "gender": gender,
        "occasion": occasion,
        "owned_items": owned_items,
        "budget_tier": budget_tier,
        "trend_keywords": trend_keywords[:12],
        "outfit_titles": outfit_titles[:5],
        "color_by_category": color_by_category or {},
        "body_profile": body_profile or {},
        "style_preferences": list(style_preferences or [])[:12],
    }
    msg = {
        "role": "user",
        "content": json.dumps(payload, ensure_ascii=False),
        "timestamp": int(time.time() * 1000),
    }
    try:
        client.v1.memories.add(
            messages=[msg],
            user_id=user_id,
            async_mode=True,
        )
    except Exception as exc:
        logger.debug("EverOS add failed: %s", exc)
