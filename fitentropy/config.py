"""Environment and constants."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _ROOT / ".env"
# 可选 .env.local（gitignore）覆盖 .env，避免误提交密钥
load_dotenv(_ENV_FILE)
load_dotenv(_ROOT / ".env.local", override=True)

QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1",
).rstrip("/")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

# OpenAI（与 Qwen 二选一；LLM_PROVIDER 可强制指定）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# auto = 有 OPENAI_API_KEY 则用 OpenAI，否则 Qwen；也可设为 openai / qwen 强制指定
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").strip().lower()


def active_llm_provider() -> str:
    """实际使用的提供方：openai | qwen。"""

    if LLM_PROVIDER == "openai":
        return "openai"
    if LLM_PROVIDER == "qwen":
        return "qwen"
    # auto
    if OPENAI_API_KEY:
        return "openai"
    return "qwen"


def llm_chat_config() -> tuple[str, str, str]:
    """返回 (base_url, api_key, model)。"""

    provider = active_llm_provider()
    if provider == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER=openai 但未设置 OPENAI_API_KEY，请在 .env 中填写"
            )
        return OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
    if not QWEN_API_KEY:
        raise RuntimeError(
            "未配置 QWEN_API_KEY；若要用 OpenAI，请设置 OPENAI_API_KEY 或 LLM_PROVIDER=openai"
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
    """关闭演示模式时的最低要求：仅需 LLM（Bright Data 可选）。"""

    return llm_configured()


def use_demo_mode() -> bool:
    """是否走演示数据。DEMO_MODE=auto 时无 LLM Key 则演示。"""

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
# 默认 model_image：打底风全身 + 防缓存参数（避免浏览器一直用旧图）
_FASHN_DEFAULT_BASE = (
    "https://images.unsplash.com/photo-1596660780693-00f011aa7231"
    "?auto=format&w=900&q=85&cb=ft20260515"
)
FASHN_DEFAULT_MODEL_IMAGE_URL = os.getenv("FASHN_DEFAULT_MODEL_IMAGE_URL", _FASHN_DEFAULT_BASE)

# 曾作为默认图的历史 URL（会话里若仍是这些，自动换成 FASHN_DEFAULT_MODEL_IMAGE_URL）
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

GENDER_OPTIONS = ("男", "女")
OCCASION_OPTIONS = ("日常", "通勤", "约会", "派对")
BUDGET_OPTIONS = ("$30以下", "$30-60", "$60-100")


def budget_yuan_to_tier(yuan: int) -> str:
    """¥ → 现有 BUDGET_OPTIONS 之一，按汇率 7 估算"""
    usd = yuan / 7
    if usd < 30:
        return "$30以下"
    if usd <= 60:
        return "$30-60"
    return "$60-100"

# 风格偏好（多选 → LLM styling_signal）
STYLE_PREFERENCE_OPTIONS: tuple[str, ...] = (
    "极简",
    "通勤利落",
    "街头休闲",
    "复古",
    "温柔女性化",
    "运动机能",
    "静奢 quiet luxury",
    "派对亮眼",
    "日系清爽",
    "美式休闲",
)

# 已有单品：按衣橱分区（UI Tab 选择，提交时压平传给模型）
OWNED_WARDROBE: dict[str, tuple[str, ...]] = {
    "上衣": (
        "T恤",
        "衬衫",
        "卫衣",
        "针织衫",
        "西装外套",
    ),
    "下装": (
        "牛仔裤",
        "休闲裤",
        "半身裙",
        "短裤",
    ),
    "连衣裙": (
        "休闲裙",
        "正式裙",
        "吊带裙",
    ),
    "鞋子": (
        "运动鞋",
        "靴子",
        "高跟鞋",
        "乐福鞋",
        "凉鞋",
    ),
    "配饰": (
        "帽子",
        "包袋",
        "墨镜",
        "围巾",
        "腰带",
    ),
    "外套": (
        "夹克",
        "风衣",
        "羽绒服",
        "毛呢大衣",
    ),
}

OWNED_WARDROBE_ORDER: tuple[str, ...] = ("上衣", "下装", "鞋子", "配饰", "外套", "连衣裙")

# 衣橱主色 / 偏好（用于搭配与零售搜索关键词）
COLOR_PREFERENCE_OPTIONS: tuple[str, ...] = (
    "黑",
    "白",
    "灰",
    "米白",
    "驼色",
    "牛仔蓝",
    "藏蓝",
    "军绿",
    "酒红",
    "粉色",
    "紫色",
    "棕色",
    "银色",
    "金色",
)


def flatten_owned_wardrobe(
    selections: dict[str, list[str]],
    colors_by_category: dict[str, list[str]] | None = None,
) -> list[str]:
    """合并各分区单品；同类所选颜色附在每件单品后，便于模型理解色盘分区。"""

    colors_by_category = colors_by_category or {}
    seen: set[str] = set()
    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        colors = [c for c in (colors_by_category.get(cat) or []) if c]
        color_seg = ""
        if colors:
            color_seg = "（色：" + "、".join(colors) + "）"
        items = selections.get(cat) or []
        for item in items:
            tagged = f"{cat}：{item}{color_seg}"
            if tagged not in seen:
                seen.add(tagged)
                out.append(tagged)
        if colors and not items:
            hint = f"{cat}·倾向色：{'、'.join(colors)}"
            if hint not in seen:
                seen.add(hint)
                out.append(hint)
    return out


def all_wardrobe_item_options() -> list[str]:
    """扁平衣橱选项（类目：单品），供 UI 单次多选。"""

    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        for item in OWNED_WARDROBE[cat]:
            out.append(f"{cat}：{item}")
    return out


def flatten_owned_selection(selected: list[str]) -> list[str]:
    """已带类目前缀的 multiselect 值，直接作为 owned_items。"""

    seen: set[str] = set()
    out: list[str] = []
    for tag in selected:
        t = (tag or "").strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def flatten_owned_picks(selections: dict[str, list[str]]) -> list[str]:
    """各分类多选 → 上衣：T恤 形式 owned_items。"""

    seen: set[str] = set()
    out: list[str] = []
    for cat in OWNED_WARDROBE_ORDER:
        for item in selections.get(cat) or []:
            tagged = f"{cat}：{item}"
            if tagged not in seen:
                seen.add(tagged)
                out.append(tagged)
    return out
