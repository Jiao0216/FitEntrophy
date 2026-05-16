"""Pre-generated FASHN mannequin templates (6 presets) for try-on model_image."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple, Union

ViewAngle = Literal["front", "side", "back"]
VIEW_ORDER: tuple[ViewAngle, ...] = ("front", "side", "back")
VIEW_LABELS: Dict[ViewAngle, str] = {
    "front": "Front",
    "side": "Side",
    "back": "Back",
}

# Project root / assets/mannequins/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANNEQUIN_DIR = PROJECT_ROOT / "assets" / "mannequins"

BODY_TYPE_SLUG: Dict[str, str] = {
    "Tall": "slim",
    "Standard": "average",
    "Curvy": "curvy",
}
BODY_TYPE_LABELS: tuple[str, ...] = tuple(BODY_TYPE_SLUG.keys())
GENDER_SLUG: Dict[str, str] = {"Female": "female", "Male": "male"}

_BODY_SUFFIX_EN: Dict[str, str] = {
    "Tall": "tall and slim body type",
    "Standard": "average body type",
    "Curvy": "curvy and full body type",
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
    ("Female", "Tall"): (
        "https://images.unsplash.com/photo-1529139574466-a303027c1d8b"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("Female", "Standard"): (
        "https://images.unsplash.com/photo-1596660780693-00f011aa7231"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("Female", "Curvy"): (
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("Male", "Tall"): (
        "https://images.unsplash.com/photo-1681686372768-3fa296d2f3e9"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("Male", "Standard"): (
        "https://images.unsplash.com/photo-1749806865395-fdc6febf58fd"
        "?auto=format&w=900&q=85&fit=crop"
    ),
    ("Male", "Curvy"): (
        "https://images.unsplash.com/photo-1674499266935-c1a522ec1973"
        "?auto=format&w=900&q=85&fit=crop"
    ),
}

_VIEW_PROMPT_SUFFIX: Dict[ViewAngle, str] = {
    "front": "facing camera directly, front view",
    "side": "full body side profile, 90 degrees to camera, neutral standing pose",
    "back": "full body back view, facing away from camera, neutral standing pose",
}

DisplaySource = Union[Path, str]


def model_create_prompt(gender: str, body_type: str, view: ViewAngle = "front") -> str:
    """Full prompt for FASHN model-create (one-time asset generation)."""

    base = _FEMALE_BASE if gender == "Female" else _MALE_BASE
    suffix = _BODY_SUFFIX_EN.get(body_type, _BODY_SUFFIX_EN["Standard"])
    angle = _VIEW_PROMPT_SUFFIX.get(view, _VIEW_PROMPT_SUFFIX["front"])
    return f"{base}, {suffix}, {angle}"


def all_presets() -> list[tuple[str, str]]:
    return [(g, b) for g in GENDER_SLUG for b in BODY_TYPE_LABELS]


def asset_basename(gender: str, body_type: str) -> str:
    g = GENDER_SLUG.get(gender, "female")
    b = BODY_TYPE_SLUG.get(body_type, "average")
    return f"{g}_{b}"


# Fallback map: body types without dedicated assets use the closest available
_BODY_TYPE_FALLBACK: Dict[str, str] = {
    "Standard": "Tall",  # "average" falls back to "slim" assets
}


def asset_paths(gender: str, body_type: str) -> list[Path]:
    stem = asset_basename(gender, body_type)
    return [MANNEQUIN_DIR / f"{stem}{ext}" for ext in (".jpg", ".jpeg", ".png", ".webp")]


def resolve_asset_path(gender: str, body_type: str) -> Path | None:
    for p in asset_paths(gender, body_type):
        if p.is_file():
            return p
    # Fallback to closest body type if no dedicated asset
    fallback_bt = _BODY_TYPE_FALLBACK.get(body_type)
    if fallback_bt:
        for p in asset_paths(gender, fallback_bt):
            if p.is_file():
                return p
    return None


def placeholder_url(gender: str, body_type: str) -> str:
    url = PLACEHOLDER_URLS.get((gender, body_type), "")
    if url:
        return url
    # Fallback
    fallback_bt = _BODY_TYPE_FALLBACK.get(body_type)
    if fallback_bt:
        return PLACEHOLDER_URLS.get((gender, fallback_bt), "")
    # Ultimate fallback
    return PLACEHOLDER_URLS.get(("Female", "Standard"), "")


def is_local_asset(gender: str, body_type: str) -> bool:
    return resolve_asset_path(gender, body_type) is not None


def has_model_image(gender: str, body_type: str) -> bool:
    """Local jpg or built-in placeholder URL either works (no FASHN Key needed)."""

    return is_local_asset(gender, body_type) or (gender, body_type) in PLACEHOLDER_URLS


def resolve_view_asset_path(gender: str, body_type: str, view: ViewAngle) -> Path | None:
    stem = asset_basename(gender, body_type)
    if view == "front":
        return resolve_asset_path(gender, body_type)
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = MANNEQUIN_DIR / f"{stem}_{view}{ext}"
        if p.is_file():
            return p
    return None


def resolve_view_source(gender: str, body_type: str, view: ViewAngle) -> DisplaySource:
    """Side/back views prefer dedicated assets; otherwise reuse front (same model)."""

    path = resolve_view_asset_path(gender, body_type, view)
    if path:
        return path
    return resolve_view_source(gender, body_type, "front") if view != "front" else placeholder_url(
        gender, body_type
    )


def has_dedicated_view_asset(gender: str, body_type: str, view: ViewAngle) -> bool:
    return resolve_view_asset_path(gender, body_type, view) is not None


def resolve_display_source(gender: str, body_type: str) -> DisplaySource:
    """Path for st.image, or HTTPS URL for placeholder preview."""

    return resolve_view_source(gender, body_type, "front")


def resolve_mannequin_views(
    gender: str, body_type: str,
) -> List[Tuple[str, DisplaySource, ViewAngle]]:
    """(view name, image source, view angle) for click-to-rotate viewer."""

    return [
        (VIEW_LABELS[v], resolve_view_source(gender, body_type, v), v)
        for v in VIEW_ORDER
    ]


def _to_data_url(source: DisplaySource) -> str:
    if isinstance(source, Path):
        return file_to_data_uri(source)
    s = str(source)
    if s.startswith(("http://", "https://", "data:")):
        return s
    return file_to_data_uri(Path(s))


def _scan_360_frame_paths(stem: str) -> list[Path]:
    frame_dir = MANNEQUIN_DIR / stem
    if frame_dir.is_dir():
        found = sorted(
            list(frame_dir.glob("frame_*.jpg"))
            + list(frame_dir.glob("frame_*.jpeg"))
            + list(frame_dir.glob("frame_*.png"))
        )
        if len(found) >= 8:
            return found
    return sorted(
        list(MANNEQUIN_DIR.glob(f"{stem}_frame_*.jpg"))
        + list(MANNEQUIN_DIR.glob(f"{stem}_frame_*.jpeg"))
        + list(MANNEQUIN_DIR.glob(f"{stem}_frame_*.png"))
    )


def resolve_mannequin_360_frames(
    gender: str,
    body_type: str,
    *,
    frame_count: int = 36,
) -> dict[str, Any]:
    """Drag-to-rotate 360° viewer data.
    - scrub: multi-frame image switching (smoothest with frame_XX resources)
    - simulate: single-image CSS rotation (compromise with only one image)
    """
    stem = asset_basename(gender, body_type)
    paths = _scan_360_frame_paths(stem)
    if len(paths) >= 8:
        frames = [
            {"url": file_to_data_uri(p), "mirror": False, "view": "orbit", "styled": False}
            for p in paths
        ]
        return {"mode": "scrub", "frames": frames}

    front = _to_data_url(resolve_view_source(gender, body_type, "front"))
    side = _to_data_url(resolve_view_source(gender, body_type, "side"))
    back = _to_data_url(resolve_view_source(gender, body_type, "back"))
    has_side = has_dedicated_view_asset(gender, body_type, "side")
    has_back = has_dedicated_view_asset(gender, body_type, "back")
    back_mirror = not has_back

    third = max(1, frame_count // 3)
    built: list[dict[str, Any]] = []
    for i in range(frame_count):
        if i < third:
            built.append(
                {
                    "url": front,
                    "view": "front",
                    "mirror": False,
                    "styled": False,
                }
            )
        elif i < 2 * third:
            built.append(
                {
                    "url": side,
                    "view": "side",
                    "mirror": False,
                    # No dedicated side view: use 3D tilt to simulate, avoid being identical to front
                    "styled": not has_side,
                }
            )
        else:
            built.append(
                {
                    "url": back,
                    "view": "back",
                    "mirror": back_mirror,
                    "styled": not has_back,
                }
            )

    return {"mode": "scrub", "frames": built}


def model_image_source_label(gender: str, body_type: str) -> str:
    stem = asset_basename(gender, body_type)
    meta = MANNEQUIN_DIR / f"{stem}.fashn"
    if meta.is_file():
        return f"FASHN model-create · {stem}.jpg"
    if is_local_asset(gender, body_type):
        return f"Local placeholder · {stem}.jpg (can regenerate with FASHN)"
    return "Online placeholder (click 'Generate Model' to save locally)"


def infer_body_type(profile: Dict[str, Any] | None, *, gender: str = "Female") -> str:
    """BMI < 18.5 → Tall; 18.5 ≤ BMI < 24 → Standard; BMI ≥ 24 → Curvy."""
    if not profile:
        return "Standard"
    h = float(profile.get("height_cm") or 0)
    w_kg = float(profile.get("weight_kg") or 0)
    if h > 0 and w_kg > 0:
        bmi = w_kg / ((h / 100) ** 2)
        if bmi < 18.5:
            return "Tall"
        if bmi < 24:
            return "Standard"
        return "Curvy"
    return "Standard"


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
        raise RuntimeError("FASHN_API_KEY not configured, cannot generate model image.")

    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)
    out = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.jpg"
    meta = MANNEQUIN_DIR / f"{asset_basename(gender, body_type)}.fashn"
    if out.is_file() and meta.is_file() and not force:
        return out

    prompt = model_create_prompt(gender, body_type, "front")
    urls = run_model_create(
        prompt,
        aspect_ratio="3:4",
        generation_mode="balanced",
        resolution="1k",
        output_format="jpeg",
        timeout=180.0,
    )
    if not urls:
        raise RuntimeError("FASHN model-create returned no image.")

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


def generate_mannequin_view_asset(
    gender: str,
    body_type: str,
    view: ViewAngle,
    *,
    force: bool = False,
) -> Path:
    """Generate one angle: assets/mannequins/{stem}_{view}.jpg"""

    from fitentropy.fashn_client import fashn_configured, run_model_create

    if view == "front":
        return generate_mannequin_asset(gender, body_type, force=force)
    if not fashn_configured():
        raise RuntimeError("FASHN_API_KEY not configured, cannot generate model image.")

    MANNEQUIN_DIR.mkdir(parents=True, exist_ok=True)
    stem = asset_basename(gender, body_type)
    out = MANNEQUIN_DIR / f"{stem}_{view}.jpg"
    if out.is_file() and not force:
        return out

    prompt = model_create_prompt(gender, body_type, view)
    urls = run_model_create(
        prompt,
        aspect_ratio="3:4",
        generation_mode="balanced",
        resolution="1k",
        output_format="jpeg",
        timeout=180.0,
    )
    if not urls:
        raise RuntimeError(f"FASHN model-create returned no image ({view}).")

    url = urls[0]
    if url.startswith("data:"):
        _header, b64 = url.split(",", 1)
        out.write_bytes(base64.b64decode(b64))
    else:
        import requests

        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        out.write_bytes(resp.content)
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


# Backward compatible alias
def has_asset(gender: str, body_type: str) -> bool:
    return has_model_image(gender, body_type)
