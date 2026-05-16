"""AgentField-wrapped entrypoint for the outfit mesh."""

from __future__ import annotations

from agentfield import Agent, AIConfig

from fitentropy import config
from fitentropy.pipeline import run_pipeline

outfit_agent = Agent(
    node_id="fitentropy",
    agentfield_server="",
    version="0.1.0",
    description="FitEntropy — reduce closet entropy with trends + LLM + retail grounding.",
    tags=["fashion", "entropy"],
    ai_config=AIConfig(
        model=(
            f"openai/{config.OPENAI_MODEL}"
            if config.active_llm_provider() == "openai"
            else config.QWEN_MODEL
        ),
        api_key=(
            config.OPENAI_API_KEY
            if config.active_llm_provider() == "openai"
            else config.QWEN_API_KEY or None
        ),
    ),
    auto_register=False,
    vc_enabled=False,
    enable_did=False,
    dev_mode=False,
)


@outfit_agent.reasoner(tags=["fashion", "entropy", "fitentropy"])
async def reduce_entropy(
    demo_mode: bool,
    user_id: str,
    gender: str,
    occasion: str,
    owned_items: list,
    budget_tier: str,
    color_by_category: dict,
    body_profile: dict | None = None,
    style_preferences: list | None = None,
) -> dict:
    """Primary mesh: orchestrates Bright Data + LLM + retail scrapes."""

    uid = (user_id or "").strip() or config.EVEROS_USER_ID
    result = run_pipeline(
        demo_mode=demo_mode,
        user_id=uid,
        gender=gender,
        occasion=occasion,
        owned_items=list(owned_items or []),
        budget_tier=budget_tier,
        color_by_category=dict(color_by_category or {}),
        body_profile=dict(body_profile or {}) or None,
        style_preferences=list(style_preferences or []) or None,
    )
    return result.model_dump()
