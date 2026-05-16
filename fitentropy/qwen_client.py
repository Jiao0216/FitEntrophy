"""LLM chat completions via OpenAI-compatible HTTP (OpenAI or DashScope Qwen)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Sequence

import requests

from fitentropy import config
from fitentropy.body_profile import slim_llm_signals

logger = logging.getLogger(__name__)


def chat_completion_json(
    messages: Sequence[Dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.4,
    timeout: int = 120,
) -> Dict[str, Any]:
    base_url, api_key, default_model = config.llm_chat_config()
    if not api_key:
        raise RuntimeError(
            "未配置语言模型 API：请在 .env 中设置 OPENAI_API_KEY 或 QWEN_API_KEY"
        )

    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: Dict[str, Any] = {
        "model": model or default_model,
        "messages": list(messages),
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    if resp.status_code >= 400:
        prov = config.llm_provider_label()
        raise RuntimeError(f"{prov} API HTTP {resp.status_code}: {resp.text[:800]}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response shape: {data!r}") from exc

    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise RuntimeError("LLM returned non-string content")

    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            return json.loads(m.group(0))
        raise


def build_outfit_prompt(
    *,
    gender: str,
    occasion: str,
    owned_items: List[str],
    budget_tier: str,
    trend_keywords: List[str],
    memory_context: str = "",
    actionbook_hints: Optional[List[str]] = None,
    color_by_category: Dict[str, List[str]] | None = None,
    body_profile: Dict[str, Any] | None = None,
    style_preferences: List[str] | None = None,
) -> List[Dict[str, str]]:
    system = (
        "You are FitEntropy, a fashion stylist AI. Reply ONLY with valid JSON matching the "
        "user schema. Be concise but specific. Use Chinese for outfit text fields "
        "(title, description, trend_rationale, missing_labels). "
        "\n\nIMPORTANT FLOW: "
        "The user does NOT have a wardrobe. Recommend 3 complete outfits FROM SCRATCH. "
        "Each outfit's missing_labels should list ALL the garments needed for that look "
        "(e.g. 上衣:白色衬衫, 下装:黑色西裤, 鞋子:乐福鞋, 配饰:手表). "
        "\n\nProduce exactly 3 outfits, each with a DIFFERENT style (e.g. 街头休闲, 优雅通勤, 运动户外). "
        "Respect budget_tier when suggesting items (approximate USD tiers). "
        "\n\nCRITICAL: missing_labels MUST include at least one wearable garment per outfit "
        "(上衣/衬衫/T恤/外套/裤子/裙子 etc) — NOT just shoes or accessories. "
        "The FIRST item in missing_labels should be the "
        "main garment (top or bottom) that completes the look — this will be used for virtual try-on. "
        "\n\nThe user JSON uses styling_signal: "
        "body (height_cm, weight_kg when present), "
        "palette_by_class (上衣/下装/连衣裙/鞋子 → colors), and style_preferences. "
        "Honor palette_by_class per class; weave color harmony into trend_rationale when natural. "
        "When style_preferences is non-empty, bias silhouettes and items toward those moods. "
        "When styling_signal.body has measurements, use them only as soft styling guidance: "
        "silhouette (腰线、裤长、肩线、裙摆长度), rise/waist placement — "
        "not guarantees. Avoid medical claims and body-shaming. "
        "Assume the shopper may preview garments on a mannequin; "
        "keep descriptions compatible with flat-lay or model try-on tools."
    )
    schema_hint = {
        "outfits": [
            {
                "title": "string",
                "description": "string",
                "trend_rationale": "string",
                "missing_labels": ["string"],
            }
        ]
    }
    actionbook_hints = actionbook_hints or []
    styling_signal = slim_llm_signals(
        body_profile=body_profile,
        color_by_category=color_by_category,
        style_preferences=style_preferences,
    )
    user_payload: Dict[str, Any] = {
        "task": "Generate 3 complete outfits from scratch (user has no existing wardrobe)",
        "gender": gender,
        "occasion": occasion,
        "wardrobe_owned": owned_items or [],
        "budget_tier": budget_tier,
        "trend_keywords": list(trend_keywords[:14]),
        "output_schema": schema_hint,
    }
    if styling_signal:
        user_payload["styling_signal"] = styling_signal
    if memory_context:
        user_payload["memory_context_from_everos"] = memory_context
    if actionbook_hints:
        user_payload["actionbook_manual_hints"] = actionbook_hints

    user = json.dumps(user_payload, ensure_ascii=False)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
