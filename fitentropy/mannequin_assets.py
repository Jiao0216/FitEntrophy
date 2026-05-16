"""Pre-generated FASHN mannequin templates (6 presets) for try-on model_image."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, Tuple, Union

# Project root / assets/mannequins/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANNEQUIN_DIR = PROJECT_ROOT / "assets" / "mannequins"

BODY_TYPE_SLUG: Dict[str, str] = {
    "高挑": "tall",
    "标准": "average",
    "丰满": "curvy",
}
BODY_TYPE_LABELS: tuple[str, ...] = tuple(BODY_TYPE_SLUG.keys())
GENDER_SLUG: Dict[str, str] = {"女": "female", "男": "male"}

_BODY_SUFFIX_EN: Dict[str, str] = {
    "高挑": "tall and slim body type",
    "标准": "average body type",
    "丰满": "curvy and full body type",
}

_FEMALE_BASE = (
    "A female fashion mannequin wearing minimal white underwear, "
    "neutral pose, standing straight, full body visible, "
    "clean white background, professional studio lighting, "
    "photorealistic, fashion photography style"
)
_MALE_BASE = (
    "A male fashion mannequin wearing minimal white underwear, "
    "neutral pose, standing straight, full body visible, "
    "clean white background, professional studio lighting, "
    "photorealistic, fashion photography style"
)

# 无 FASHN Key 时用于界面预览 / 试穿 model_image（公网 Unsplash，全身打底风）
# 有 Key 后可用 scripts/generate_mannequin_assets.py 生成正式图并覆盖本地 jpg
PLACEHOLDER_URLS: Dict[tuple[str, str], str] = {
    ("女", "高挑"): (
        "https://images.unsplash.com/photo-1529139574466-a303027c1d8b"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("女", "标准"): (
        "https://images.unsplash.com/photo-1596660780693-00f011aa7231"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("女", "丰满"): (
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    # 男：全身、内裤/极简打底、站姿（演示占位；正式图用 model-create）
    ("男", "高挑"): (
        "https://images.unsplash.com/photo-1681686372768-3fa296d2f3e9"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("男", "标准"): (
        "https://images.unsplash.com/photo-1749806865395-fdc6febf58fd"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("男", "丰满"): (
        "https://images.unsplash.com/photo-1674499266935-c1a522ec1973"
        "?auto=format&w=900&q=85&fit=crop"
    ),
}

DisplaySource = Union[Path, str]


def model_create_prompt(gender: str, body_type: str) -> str:
    """Full prompt for FASHN model-create (one-time asset generation)."""

    base = _FEMALE_BASE if gender == "女" else _MALE_BASE
    suffix = _BODY_SUFFIX_EN.get(body_type, _BODY_SUFFIX_EN["标准"])
    return f"{base}, {suffix}"


def all_presets() -> list[tuple[str, str]]:
    return [(g, b) for g in GENDER_SLUG for b in BODY_TYPE_LABELS]


def asset_basename(gender: str, body_type: str) -> str:
    g = GENDER_SLUG.get(gender, "female")
    b = BODY_TYPE_SLUG.get(body_type, "average")
    return f"{g}_{b}"


def asset_paths(gender: str, body_type: str) -> list[Path]:
    stem = asset_basename(gender, body_type)
    return [MANNEQUIN_DIR / f"{stem}{ext}" for ext in (".jpg", ".jpeg", ".png", ".webp")]


def resolve_asset_path(gender: str, body_type: str) -> Path | None:
    for p in asset_paths(gender, body_type):
        if p.is_file():
            return p
    return None


def placeholder_url(gender: str, body_type: str) -> str:
    return PLACEHOLDER_URLS.get((gender, body_type), PLACEHOLDER_URLS[("女", "标准")])


def is_local_asset(gender: str, body_type: str) -> bool:
    return resolve_asset_path(gender, body_type) is not None


def has_model_image(gender: str, body_type: str) -> bool:
    """本地 jpg 或内置占位 URL 任一可用即为 True（无需 FASHN Key）。"""

    return is_local_asset(gender, body_type) or (gender, body_type) in PLACEHOLDER_URLS


def resolve_display_source(gender: str, body_type: str) -> DisplaySource:
    """Path for st.image, or HTTPS URL for placeholder preview."""

    path = resolve_asset_path(gender, body_type)
    if path:
        return path
    return placeholder_url(gender, body_type)


def model_image_source_label(gender: str, body_type: str) -> str:
    stem = asset_basename(gender, body_type)
    meta = MANNEQUIN_DIR / f"{stem}.fashn"
    if meta.is_file():
        return f"FASHN model-create · {stem}.jpg"
    if is_local_asset(gender, body_type):
        return f"本地占位图 · {stem}.jpg（可用 FASHN 重新生成）"
    return "在线占位图（点击「FASHN 生成模特」保存到本地）"


def infer_body_type(profile: Dict[str, Any] | None, *, gender: str = "女") -> str:
    if not profile:
        return "标准"
    h = float(profile.get("height_cm") or 0)
    w_kg = float(profile.get("weight_kg") or 0)
    bust = float(profile.get("bust_cm") or 0)
    waist = float(profile.get("waist_cm") or 0)
    hip = float(profile.get("hip_cm") or 0)

    bmi = (w_kg / ((h / 100) ** 2)) if h > 0 and w_kg > 0 else 0.0
    wh = (waist / hip) if waist > 0 and hip > 0 else 0.0

    if h >= 172 and bmi and bmi < 22:
        return "高挑"
    if bmi >= 26 or (wh >= 0.88 and hip >= 95):
        return "丰满"
    if h >= 168 and bmi and bmi <= 21:
        return "高挑"
    if bust >= 95 and hip >= 100 and waist >= 78:
        return "丰满"
    return "标准"


def file_to_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith("image/"):
        mime = "image/jpeg"
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def generate_mannequin_asset(
    gender: str,
    body_type: str,
    *,
    force: bool = False,
) -> Path:
    """Call FASHN model-create and save assets/mannequins/{gender}_{body}.jpg."""

    from fitentropy.fashn_client import fashn_configured, run_model_create

    if not fashn_configured():
        raise RuntimeError("未配置 FASHN_API_KEY，无法生成模特图。")

    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)
    out = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.jpg"
    meta = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.fashn"
    if out.is_file() and meta.is_file() and not force:
        return out

    prompt = model_create_prompt(gender, body_type)
    urls = run_model_create(
        prompt,
        aspect_ratio="3:4",
        generation_mode="balanced",
        resolution="1k",
        output_format="jpeg",
        timeout=180.0,
    )
    if not urls:
        raise RuntimeError("FASHN model-create 未返回图片。")

    url = urls[0]
    if url.startswith("data:"):
        _header, b64 = url.split(",", 1)
        out.write_bytes(base64.b64decode(b64))
    else:
        import requests

        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        out.write_bytes(resp.content)

    meta.write_text("fashn model-create\n", encoding="utf-8")
    return out


def download_preset_to_local(gender: str, body_type: str) -> Path:
    """Save placeholder URL as assets/mannequins/{gender}_{body}.jpg (no FASHN Key)."""

    import requests

    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)
    out = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.jpg"
    url = placeholder_url(gender, body_type)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out.write_bytes(resp.content)
    return out


def model_image_for_tryon(gender: str, body_type: str) -> Tuple[str, str]:
    """Return (model_image for FASHN API as data-uri or URL, human-readable source label)."""

    path = resolve_asset_path(gender, body_type)
    if path:
        return file_to_data_uri(path), model_image_source_label(gender, body_type)
    return placeholder_url(gender, body_type), model_image_source_label(gender, body_type)


# 兼容旧调用
def has_asset(gender: str, body_type: str) -> bool:
    return has_model_image(gender, body_type)
