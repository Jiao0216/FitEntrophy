"""Environment and constants."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _ROOT / ".env"
# Optional .env.local (gitignore) overrides .env to avoid committing secrets
load_dotenv(_ENV_FILE)
load_dotenv(_ROOT / ".env.local", override=True)

QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
).rstrip("/")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

# OpenAI (alternative to Qwen; LLM_PROVIDER can force one)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# auto = use OpenAI if OPENAI_API_KEY exists, else Qwen; can also set openai / qwen to force
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").strip().lower()


def active_llm_provider() -> str:
    """Active provider: openai | qwen."""

    if LLM_PROVIDER == "openai":
        return "openai"
    if LLM_PROVIDER == "qwen":
        return "qwen"
    # auto
    if OPENAI_API_KEY:
        return "openai"
    return "qwen"


def llm_chat_config() -> tuple[str, str, str]:
    """Return (base_url, api_key, model)."""

    provider = active_llm_provider()
    if provider == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. Please add it to .env"
            )
        return OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
    if not QWEN_API_KEY:
        raise RuntimeError(
            "QWEN_API_KEY not configured. To use OpenAI, set OPENAI_API_KEY or LLM_PROVIDER=openai"
        )
    return QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL


def llm_provider_label() -> str:
    p = active_llm_provider()
    return "OpenAI" if p == "openai" else "Qwen"


def llm_model_label() -> str:
    return OPENAI_MODEL if active_llm_provider() == "openai" else QWEN_MODEL


def llm_configured() -> bool:
    p = active_llm_provider()
    if p == "openai":
        return bool(OPENAI_API_KEY)
    return bool(QWEN_API_KEY)


def brightdata_configured() -> bool:
    return bool(BRIGHTDATA_API_KEY)


def live_pipeline_ready() -> bool:
    """Minimum requirement for live mode: LLM only (Bright Data optional)."""

    return llm_configured()


def use_demo_mode() -> bool:
    """Whether to use demo data. DEMO_MODE=auto uses demo when no LLM key."""

    raw = os.getenv("DEMO_MODE", "auto").strip().lower()
    if raw in ("1", "true", "yes", "demo"):
        return True
    if raw in ("0", "false", "no", "live"):
        return False
    return not llm_configured()

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE", "web_unlocker1")
BRIGHTDATA_REQUEST_URL = "https://api.brightdata.com/request"

EVEROS_API_KEY = os.getenv("EVEROS_API_KEY", "")
EVEROS_USER_ID = os.getenv("EVEROS_USER_ID", "agent-forge-demo")

# FASHN Virtual Try-On (https://docs.fashn.ai/) — optional; used from UI when URLs are provided
FASHN_API_KEY = os.getenv("FASHN_API_KEY", "")
FASHN_API_BASE = os.getenv("FASHN_API_BASE", "https://api.fashn.ai").rstrip("/")
# Default model_image: full-body base layer + cache-buster param
_FASHN_DEFAULT_BASE = (
    "https://images.unsplash.com/photo-1596660780693-00f011aa7231"
    "?auto=format&w=900&q=85&cb=ft20260515"
)
FASHN_DEFAULT_MODEL_IMAGE_URL = os.getenv("FASHN_DEFAULT_MODEL_IMAGE_URL", _FASHN_DEFAULT_BASE)

# Legacy default URLs (auto-reset if still in session)
FASHN_LEGACY_MODEL_IMAGE_URLS: frozenset[str] = frozenset(
    {
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&w=900&q=85",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&w=900&q=85",
        "https://images.unsplash.com/photo-1596660780693-00f011aa7231?auto=format&w=900&q=85",
    }
)


def fashn_model_session_should_reset(stored: str) -> bool:
    """True when stored URL is a shipped legacy default (or obvious variant), not user custom."""

    s = (stored or "").strip()
    if not s or s == FASHN_DEFAULT_MODEL_IMAGE_URL:
        return False
    if s in FASHN_LEGACY_MODEL_IMAGE_URLS:
        return True
    if "images.unsplash.com" not in s:
        return False
    if "1515886657613" in s or "1518611012118" in s:
        return True
    if "1596660780693" in s and "cb=ft20260515" not in s:
        return True
    return False


ACTIONBOOK_CLI_HINTS = os.getenv("ACTIONBOOK_CLI_HINTS", "0").lower() in (
    "1",
    "true",
    "yes",
)

# Trend / retail targets (English locales for stable product URLs)
TREND_SOURCES = (
    "https://www.pinterest.com/today/",
    "https://www.whowhatwear.com/fashion-trends",
)

RETAIL_SEARCH = {
    "Zara": "https://www.zara.com/us/en/search?searchTerm={q}",
    "H&M": "https://www2.hm.com/en_us/search-results.html?q={q}",
    "UNIQLO": "https://www.uniqlo.com/us/en/search?q={q}",
}

GENDER_OPTIONS = ("Male", "Female")
OCCASION_OPTIONS = ("Daily", "Work", "Date", "Party")
BUDGET_OPTIONS = ("Under $30", "$30-60", "$60-100")


def budget_yuan_to_tier(yuan: int) -> str:
    """Convert CNY to BUDGET_OPTIONS tier (exchange rate ~7)."""
    usd = yuan / 7
    if usd < 30:
        return "Under $30"
    if usd <= 60:
        return "$30-60"
    return "$60-100"

# Style preferences (multi-select → LLM styling_signal)
STYLE_PREFERENCE_OPTIONS: tuple[str, ...] = (
    "Minimalist",
    "Sharp Workwear",
    "Street Casual",
    "Retro",
    "Soft Feminine",
    "Sporty Utility",
    "Quiet Luxury",
    "Party Glam",
    "Japanese Clean",
    "American Casual",
)

# Wardrobe categories: items per section (UI tab selection, flattened on submit)
OWNED_WARDROBE: dict[str, tuple[str, ...]] = {
    "Tops": (
        "T-shirt",
        "Shirt",
        "Hoodie",
        "Knitwear",
        "Blazer",
    ),
    "Bottoms": (
        "Jeans",
        "Casual Pants",
        "Skirt",
        "Shorts",
    ),
    "Dresses": (
        "Casual Dress",
        "Formal Dress",
        "Slip Dress",
    ),
    "Shoes": (
        "Sneakers",
        "Boots",
        "Heels",
        "Loafers",
        "Sandals",
    ),
    "Accessories": (
        "Hat",
        "Bag",
        "Sunglasses",
        "Scarf",
        "Belt",
    ),
    "Outerwear": (
        "Jacket",
        "Trench Coat",
        "Puffer",
        "Wool Coat",
    ),
}

OWNED_WARDROBE_ORDER: tuple[str, ...] = ("Tops", "Bottoms", "Shoes", "Accessories", "Outerwear", "Dresses")

# Color preferences (for outfit matching and retail search keywords)
COLOR_PREFERENCE_OPTIONS: tuple[str, ...] = (
    "Black",
    "White",
    "Gray",
    "Off-White",
    "Camel",
    "Denim Blue",
    "Navy",
    "Olive",
    "Burgundy",
    "Pink",
    "Purple",
    "Brown",
    "Silver",
    "Gold",
)


def flatten_owned_wardrobe(
    selections: dict[str, list[str]],
    colors_by_category: dict[str, list[str]] | None = None,
) -> list[str]:
    """Merge selections across categories; attach colors per item for model context."""

    colors_by_category = colors_by_category or {}
    seen: set[str] = set()
    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        colors = [c for c in (colors_by_category.get(cat) or []) if c]
        color_seg = ""
        if colors:
            color_seg = " (colors: " + ", ".join(colors) + ")"
        items = selections.get(cat) or []
        for item in items:
            tagged = f"{cat}: {item}{color_seg}"
            if tagged not in seen:
                seen.add(tagged)
                out.append(tagged)
        if colors and not items:
            hint = f"{cat} preferred colors: {', '.join(colors)}"
            if hint not in seen:
                seen.add(hint)
                out.append(hint)
    return out


def all_wardrobe_item_options() -> list[str]:
    """Flat wardrobe options (category: item) for UI multi-select."""

    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        for item in OWNED_WARDROBE[cat]:
            out.append(f"{cat}: {item}")
    return out


def flatten_owned_selection(selected: list[str]) -> list[str]:
    """Multi-select values already prefixed with category, used as owned_items directly."""

    seen: set[str] = set()
    out: list[str] = []
    for tag in selected:
        t = (tag or "").strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def flatten_owned_picks(selections: dict[str, list[str]]) -> list[str]:
    """Category multi-select → 'Tops: T-shirt' style owned_items."""

    seen: set[str] = set()
    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        for item in selections.get(cat) or []:
            tagged = f"{cat}: {item}"
            if tagged not in seen:
                seen.add(tagged)
                out.append(tagged)
    return out
