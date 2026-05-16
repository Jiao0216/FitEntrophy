"""User-reported body measurements for styling / fit hints (not medical)."""

from __future__ import annotations

from typing import Any, Dict, List


def normalize_body_profile(
    *,
    height_cm: int | float | None = None,
    weight_kg: int | float | None = None,
    bust_cm: int | float | None = None,
    waist_cm: int | float | None = None,
    hip_cm: int | float | None = None,
) -> Dict[str, Any]:
    """Drop zeros / negatives; keep compact numbers for JSON → LLM."""

    out: Dict[str, Any] = {}

    def _add(key: str, val: int | float | None) -> None:
        if val is None:
            return
        try:
            f = float(val)
        except (TypeError, ValueError):
            return
        if f <= 0:
            return
        out[key] = int(f) if f == int(f) else round(f, 1)

    _add("height_cm", height_cm)
    _add("weight_kg", weight_kg)
    _add("bust_cm", bust_cm)
    _add("waist_cm", waist_cm)
    _add("hip_cm", hip_cm)
    return out


def body_profile_line(profile: Dict[str, Any] | None) -> str:
    """Short line for logs or secondary prompts."""

    if not profile:
        return ""
    parts: list[str] = []
    if h := profile.get("height_cm"):
        parts.append(f"Height ~{h}cm")
    if w := profile.get("weight_kg"):
        parts.append(f"Weight ~{w}kg")
    if b := profile.get("bust_cm"):
        parts.append(f"Bust ~{b}cm")
    if wst := profile.get("waist_cm"):
        parts.append(f"Waist ~{wst}cm")
    if hip := profile.get("hip_cm"):
        parts.append(f"Hip ~{hip}cm")
    return "; ".join(parts) if parts else ""


def slim_llm_signals(
    *,
    body_profile: Dict[str, Any] | None,
    color_by_category: Dict[str, List[str]] | None,
    style_preferences: List[str] | None,
) -> Dict[str, Any]:
    """Single compact object for the LLM: drop empty lists / nulls."""

    sig: Dict[str, Any] = {}
    if body_profile:
        body = {k: v for k, v in body_profile.items() if v not in (None, "", [], {})}
        if body:
            sig["body"] = body
    if color_by_category:
        pal = {
            k: [x for x in (v or []) if x]
            for k, v in color_by_category.items()
        }
        pal = {k: v for k, v in pal.items() if v}
        if pal:
            sig["palette_by_class"] = pal
    if style_preferences:
        styles = [str(s).strip() for s in style_preferences if str(s).strip()]
        if styles:
            sig["style_preferences"] = styles[:10]
    return sig


def mannequin_svg_html(profile: Dict[str, Any] | None) -> str:
    """Simple geometric 'dummy' from numbers (not a scan). Dark-theme friendly SVG."""

    if not profile:
        return ""
    h = float(profile.get("height_cm") or 0)
    w_kg = float(profile.get("weight_kg") or 0)
    bust = float(profile.get("bust_cm") or 0)
    waist = float(profile.get("waist_cm") or 0)
    hip = float(profile.get("hip_cm") or 0)
    if not any(x > 0 for x in (h, w_kg, bust, waist, hip)):
        return ""

    # Heuristic widths in SVG units (no medical claim)
    bust_ref = bust if bust > 0 else (86.0 + (w_kg - 58.0) * 0.35 if w_kg > 0 else 86.0)
    waist_ref = waist if waist > 0 else (68.0 + (w_kg - 55.0) * 0.25 if w_kg > 0 else 70.0)
    hip_ref = hip if hip > 0 else (92.0 + (w_kg - 58.0) * 0.3 if w_kg > 0 else 92.0)

    shoulder = 34.0 + (bust_ref - 82.0) * 0.22
    shoulder = max(28.0, min(52.0, shoulder))
    waist_w = 20.0 + (waist_ref - 62.0) * 0.18
    waist_w = max(16.0, min(38.0, waist_w))
    hip_w = 26.0 + (hip_ref - 88.0) * 0.16
    hip_w = max(22.0, min(46.0, hip_w))

    # subtle height stretch for long legs in drawing only
    leg_scale = 1.0
    if h > 0:
        leg_scale = 0.92 + (h - 160.0) * 0.002
        leg_scale = max(0.88, min(1.12, leg_scale))

    leg_len = 78.0 * leg_scale

    return f"""
<div style="display:flex;justify-content:center;padding:0.5rem 0;">
  <svg viewBox="0 0 120 260" width="200" height="420" role="img" aria-label="Body outline mannequin"
       style="max-width:min(220px,100%);height:auto;filter:drop-shadow(0 6px 18px rgba(0,0,0,0.35));">
    <rect width="120" height="260" rx="16" fill="#111827"/>
    <circle cx="60" cy="28" r="14" fill="#94a3b8" stroke="#5eead4" stroke-width="1.2"/>
    <line x1="60" y1="42" x2="60" y2="54" stroke="#64748b" stroke-width="3" stroke-linecap="round"/>
    <path d="M {60 - shoulder:.1f} 54 L {60 - waist_w:.1f} 118 L {60 + waist_w:.1f} 118 L {60 + shoulder:.1f} 54 Z"
          fill="#334155" stroke="#5eead4" stroke-width="0.8" opacity="0.95"/>
    <path d="M {60 - waist_w:.1f} 118 L {60 - hip_w:.1f} 168 L {60 + hip_w:.1f} 168 L {60 + waist_w:.1f} 118 Z"
          fill="#1e293b" stroke="#5eead4" stroke-width="0.8" opacity="0.95"/>
    <line x1="60" y1="168" x2="48" y2="{168 + leg_len:.1f}" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
    <line x1="60" y1="168" x2="72" y2="{168 + leg_len:.1f}" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
    <text x="60" y="252" text-anchor="middle" fill="#94a3b8" font-size="9" font-family="system-ui,sans-serif">
      Body Outline · Not a Scan
    </text>
  </svg>
</div>
""".strip()
