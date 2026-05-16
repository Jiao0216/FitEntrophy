"""FitEntropy dashboard theme (HTML + CSS helpers for Streamlit)."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Union

THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', system-ui, sans-serif; }
[data-testid="stAppViewContainer"], section[data-testid="stMain"] { background: #08060f !important; }
header[data-testid="stHeader"], [data-testid="stHeader"] {
  background: transparent !important; border: none !important;
}
[data-testid="stDecoration"] { display: none !important; }
.stApp {
  background: #08060f;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.22), transparent),
    radial-gradient(ellipse 40% 30% at 100% 0%, rgba(59, 130, 246, 0.12), transparent),
    radial-gradient(ellipse 30% 25% at 0% 100%, rgba(59, 130, 246, 0.10), transparent);
  color: #e2e8f0;
}
.block-container { padding-top: 0.5rem; max-width: 1280px; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
  /* sidebar visible — contains demo toggle and key status */
}
.ft-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.5rem 0 1.25rem; border-bottom: 1px solid rgba(139,92,246,0.12);
  margin-bottom: 1.5rem;
}
.ft-logo { display: flex; align-items: center; gap: 0.6rem; }
.ft-logo-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; font-size: 1rem;
  box-shadow: 0 0 24px rgba(139, 92, 246, 0.45);
}
.ft-logo-text {
  font-family: 'JetBrains Mono', monospace; font-weight: 600;
  font-size: 1.15rem; color: #f8fafc;
}
.ft-nav-links { display: flex; gap: 1.4rem; }
.ft-nav-tab {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  color: #94a3b8; font-size: 0.74rem; text-decoration: none; padding-bottom: 4px;
}
.ft-nav-tab.active { color: #c4b5fd; border-bottom: 2px solid #8b5cf6; }
.ft-nav-tab .ft-nav-icon { font-size: 1.05rem; }
.ft-hero-title {
  text-align: center; font-size: 2rem; font-weight: 500; color: #f1f5f9;
  max-width: 46rem; margin: 0 auto 1.25rem; line-height: 1.35;
}
.ft-hero-accent { color: #a78bfa; font-weight: 500; }
.ft-section {
  background: rgba(15, 12, 24, 0.75); border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 16px; padding: 1.35rem 1.5rem; margin-bottom: 1.25rem;
}
.ft-section-head { font-size: 1rem; font-weight: 600; color: #f8fafc; margin: 0 0 1rem; }
.ft-section-head em { color: #8b5cf6; font-style: normal; }
.ft-soft-note {
  font-size: 0.88rem; color: #cbd5e1; margin: 0 0 1rem; line-height: 1.5;
}
.ft-footer {
  text-align: center; padding: 1.5rem 0 2rem;
  border-top: 1px solid rgba(139, 92, 246, 0.12);
  font-size: 0.82rem; color: #64748b;
}
/* ── Section badge header ─────────────────────────────────────────────────── */
.ft-section-badge-head { font-size: 1rem; font-weight: 500; color: #f8fafc; margin: 0 0 1rem; }
.ft-section-badge {
  display: inline-block; width: 30px; height: 30px; border-radius: 8px;
  border: 1px solid rgba(139,92,246,0.35); color: #a78bfa;
  font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
  line-height: 30px; text-align: center;
  margin-right: 0.55rem; vertical-align: -7px;
}
/* ── Hero model image ─────────────────────────────────────────────────────── */
.ft-hero-model {
  max-width: 320px; margin: 1rem auto 0.5rem; aspect-ratio: 3/4;
  border-radius: 16px;
  background: radial-gradient(ellipse at 50% 60%, rgba(139,92,246,0.4) 0%, rgba(15,12,24,0.95) 70%);
  border: 1px solid rgba(139,92,246,0.25); overflow: hidden; position: relative;
}
.ft-hero-model-label {
  position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
  padding: 0.3rem 0.7rem; border-radius: 8px;
  background: rgba(15,12,24,0.78); border: 1px solid rgba(139,92,246,0.3);
  font-size: 0.7rem; color: #c4b5fd;
  font-family: 'JetBrains Mono', monospace; white-space: nowrap;
}
.ft-hero-model-caption { text-align: center; font-size: 0.78rem; color: #64748b; margin: 0 auto 1.75rem; }
/* ── Look cards ────────────────────────────────────────────────────────────── */
.ft-look-card {
  background: rgba(20,16,32,0.7); border: 1px solid rgba(139,92,246,0.25);
  border-radius: 14px; padding: 1rem 0.95rem; display: flex; flex-direction: column; height: 100%;
}
.ft-look-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.7rem; }
.ft-look-num-badge {
  padding: 0.25rem 0.55rem; border-radius: 6px;
  background: rgba(139,92,246,0.85); color: #fff;
  font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 500;
}
.ft-look-star { color: #a78bfa; font-size: 0.95rem; cursor: pointer; }
.ft-look-title-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.3rem; }
.ft-look-title { font-size: 1rem; font-weight: 500; color: #f8fafc; }
.ft-look-tag {
  font-size: 0.62rem; padding: 0.16rem 0.42rem; border-radius: 5px;
  background: rgba(139,92,246,0.22); color: #ddd6fe;
}
.ft-look-desc {
  font-size: 0.74rem; color: #94a3b8; line-height: 1.45; margin: 0 0 0.85rem;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.ft-look-accessories-label {
  font-size: 0.62rem; color: #64748b; text-transform: uppercase;
  letter-spacing: 0.08em; margin-bottom: 0.35rem;
}
.ft-look-accessory {
  flex: 1; padding: 0.3rem; border: 1px solid rgba(139,92,246,0.15);
  border-radius: 7px; display: flex; align-items: center; gap: 0.35rem; min-width: 0;
}
.ft-look-accessory img, .ft-look-accessory .placeholder {
  width: 24px; height: 24px; border-radius: 5px;
  background: rgba(167,139,250,0.18); flex-shrink: 0; object-fit: cover;
}
.ft-look-accessory .meta { min-width: 0; }
.ft-look-accessory .name { font-size: 0.62rem; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ft-look-accessory .price { font-size: 0.62rem; color: #a78bfa; }
.ft-look-detail-btn {
  margin-top: auto; width: 100%; padding: 0.55rem; border-radius: 9px;
  background: transparent; border: 1px solid rgba(139,92,246,0.45); color: #c4b5fd;
  font-size: 0.75rem; cursor: pointer; font-family: inherit;
}
.ft-look-detail-btn:hover { background: rgba(139,92,246,0.15); }
/* ── Missing items ─────────────────────────────────────────────────────────── */
.ft-missing-title {
  font-size: 0.72rem; font-weight: 600; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.08em; margin: 0.75rem 0 0.35rem;
}
.ft-missing-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0; border-top: 1px solid rgba(139, 92, 246, 0.1);
  font-size: 0.8rem; color: #cbd5e1;
}
.ft-missing-item a { color: #a78bfa; text-decoration: none; font-weight: 600; font-size: 0.75rem; }
/* ── Step rail ─────────────────────────────────────────────────────────────── */
.ft-rail-wrap { border-left: 2px solid rgba(139, 92, 246, 0.35); padding-left: 1rem; }
.ft-rail-step { margin-bottom: 1.5rem; }
.ft-rail-num { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #8b5cf6; }
.ft-rail-title { font-size: 0.95rem; font-weight: 600; color: #f8fafc; }
.ft-rail-sub { font-size: 0.72rem; color: #64748b; text-transform: uppercase; }
.ft-rail-step.active .ft-rail-title { color: #c4b5fd; }
/* ── Form submit button ────────────────────────────────────────────────────── */
.stFormSubmitButton > button {
  width: 100% !important; padding: 0.75rem !important; border-radius: 12px !important;
  background: linear-gradient(135deg, #6d28d9, #8b5cf6, #a78bfa) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 0 24px rgba(139, 92, 246, 0.4) !important;
}
label { color: #e2e8f0 !important; }
[data-testid="stWidgetLabel"] p {
  color: #94a3b8 !important; font-size: 0.72rem !important;
  letter-spacing: 0.04em !important; text-transform: uppercase !important;
}
/* ── Tabs as icon cards ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 0.55rem !important; background: transparent !important; }
.stTabs [data-baseweb="tab"] {
  flex: 1 !important; padding: 0.65rem 0.5rem !important;
  border-radius: 10px !important; border: 1px solid rgba(139,92,246,0.2) !important;
  background: transparent !important; font-size: 0.8rem !important; color: #94a3b8 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: rgba(139,92,246,0.22) !important; border-color: #8b5cf6 !important; color: #ddd6fe !important;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }
/* ── Number inputs dark theme ─────────────────────────────────────────────── */
[data-testid="stNumberInput"] [data-baseweb="input"] {
  background: rgba(15,12,24,0.9) !important;
  border: 1px solid rgba(139,92,246,0.25) !important; border-radius: 10px !important;
}
[data-testid="stNumberInput"] [data-baseweb="input"] input { color: #f1f5f9 !important; }
[data-testid="stNumberInput"] [data-baseweb="input"] button { color: #a78bfa !important; background: transparent !important; border: none !important; }
/* ── Radio buttons as pill chips ──────────────────────────────────────────── */
[data-testid="stRadio"] > div[role="radiogroup"] { gap: 0.45rem !important; }
[data-testid="stRadio"] label {
  border: 1px solid rgba(139,92,246,0.25) !important; border-radius: 10px !important;
  padding: 0.4rem 0.8rem !important; background: transparent !important;
  cursor: pointer !important; transition: all 0.15s !important;
}
[data-testid="stRadio"] label:has(input[type="radio"]:checked) {
  background: rgba(139,92,246,0.22) !important; border-color: #8b5cf6 !important; color: #ddd6fe !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { color: inherit !important; font-size: 0.82rem !important; text-transform: none !important; letter-spacing: 0 !important; }
[data-testid="stRadio"] input[type="radio"] { display: none !important; }
[data-baseweb="select"] > div {
  background: rgba(15, 12, 24, 0.9) !important;
  border-color: rgba(139, 92, 246, 0.25) !important; border-radius: 10px !important;
}
div[data-testid="stImage"] img {
  border-radius: 16px 16px 0 0 !important; border: 1px solid rgba(139, 92, 246, 0.2) !important;
}
.ft-profile-preview [data-testid="stImage"] {
  max-width: 200px !important;
  margin: 0 auto !important;
}
.ft-profile-preview [data-testid="stImage"] img {
  max-width: 200px !important;
  width: 200px !important;
  margin: 0 auto !important;
  display: block !important;
  border-radius: 12px !important;
}
"""

BODY_TYPE_EN = {"Tall": ("Tall / Slim", "↗"), "Standard": ("Standard", "◎"), "Curvy": ("Fuller", "●")}
GENDER_EN = {"Male": "Male", "Female": "Female"}
WARDROBE_ICON = {"Tops": "👕", "Bottoms": "👖", "Dresses": "👗", "Shoes": "👟", "Accessories": "👜", "Outerwear": "🧥"}
OCCASION_EN = {"Daily": "Daily", "Work": "Work", "Date": "Date", "Party": "Party"}


def inject_theme() -> None:
    import streamlit as st

    st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)


def render_nav(active: str = "Dashboard") -> None:
    import streamlit as st

    _tabs = [("▦", "Dashboard"), ("👕", "Wardrobe"), ("✨", "Outfits"), ("◉", "Profile")]
    items = "".join(
        f'<a href="#" class="ft-nav-tab{" active" if label == active else ""}">'
        f'<span class="ft-nav-icon">{icon}</span><span>{label}</span></a>'
        for icon, label in _tabs
    )
    st.markdown(
        f'<header class="ft-nav">'
        f'<div class="ft-logo"><div class="ft-logo-icon">F</div>'
        f'<span class="ft-logo-text">FitEntropy</span></div>'
        f'<nav class="ft-nav-links">{items}</nav>'
        f'</header>',
        unsafe_allow_html=True,
    )


def render_hero(slogan: str) -> None:
    import streamlit as st

    highlighted = (
        html.escape(slogan)
        .replace("Win the date", '<span class="ft-hero-accent">Win the date</span>')
        .replace(". ", '.<br>')
    )
    st.markdown(f'<h1 class="ft-hero-title">{highlighted}</h1>', unsafe_allow_html=True)


def render_step_rail(active_step: int) -> None:
    import streamlit as st

    steps = [(1, "Who are you", "Profile"), (2, "What do you have", "Wardrobe"), (3, "Your Outfits", "Results")]
    inner = []
    for num, zh, en in steps:
        cls = "ft-rail-step active" if num == active_step else "ft-rail-step"
        inner.append(
            f'<div class="{cls}"><div class="ft-rail-num">{num}</div>'
            f'<div class="ft-rail-title">{html.escape(zh)}</div>'
            f'<div class="ft-rail-sub">{html.escape(en)}</div></div>'
        )
    st.markdown(f'<div class="ft-rail-wrap">{"".join(inner)}</div>', unsafe_allow_html=True)


def render_footer() -> None:
    import streamlit as st

    st.markdown(
        '<footer class="ft-footer">FitEntropy · Less Random, More Style</footer>',
        unsafe_allow_html=True,
    )


def accessory_thumbs_html(offers: list) -> str:
    """Two-slot accessory row for look cards."""
    items = [o for o in (offers or []) if isinstance(o, dict)][:2]

    _placeholder = (
        '<div class="ft-look-accessory">'
        '<div class="placeholder"></div>'
        '<div class="meta"><div class="name">—</div><div class="price">—</div></div>'
        '</div>'
    )

    def _slot(off: dict) -> str:
        prod = off.get("product") or {}
        name = html.escape(str(prod.get("name") or off.get("label") or "—")[:22])
        price = html.escape(str(prod.get("price_display") or "—"))
        img_url = prod.get("image_url") or ""
        thumb = (
            f'<img src="{html.escape(img_url)}">'
            if img_url
            else '<div class="placeholder"></div>'
        )
        return (
            f'<div class="ft-look-accessory">{thumb}'
            f'<div class="meta"><div class="name">{name}</div><div class="price">{price}</div></div>'
            f'</div>'
        )

    slots = [_slot(o) for o in items]
    while len(slots) < 2:
        slots.append(_placeholder)
    return f'<div style="display:flex;gap:0.4rem;margin-bottom:0.75rem;">{"".join(slots)}</div>'


def missing_items_html(offers: list, missing_labels: list) -> str:
    rows = []
    if offers:
        for off in offers[:4]:
            if not isinstance(off, dict):
                continue
            label = html.escape(str(off.get("label") or ""))
            prod = off.get("product") or {}
            price = html.escape(str(prod.get("price_display") or "—"))
            url = prod.get("url") or ""
            link = f'<a href="{html.escape(url)}" target="_blank">Shop Now</a>' if url else ""
            rows.append(
                f'<div class="ft-missing-item"><span>{label} · {price}</span>{link}</div>'
            )
    elif missing_labels:
        for label in missing_labels[:4]:
            rows.append(f'<div class="ft-missing-item"><span>{html.escape(label)}</span></div>')
    if not rows:
        rows.append('<div class="ft-missing-item"><span>—</span></div>')
    return '<div class="ft-missing-title">Missing Items</div>' + "".join(rows)


# ── Interactive image components ─────────────────────────────────────────────

ImageSource = Union[Path, str]


def _image_url(src: ImageSource) -> str:
    from fitentropy.mannequin_assets import file_to_data_uri

    if isinstance(src, Path):
        return file_to_data_uri(src)
    s = str(src)
    if s.startswith(("http://", "https://", "data:")):
        return s
    return file_to_data_uri(Path(s))


def render_image_360(
    viewer_data: dict,
    *,
    width: int = 220,
    height: int | None = None,
    key: str = "ft360",
) -> None:
    """Drag horizontally to scrub 360° mannequin views."""
    import streamlit.components.v1 as components

    if height is None:
        height = int(width * 1.4) + 36

    card_id = re.sub(r"[^a-zA-Z0-9_-]", "", key) or "ft360"
    data_json = json.dumps(viewer_data, ensure_ascii=False)

    doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: transparent; overflow: hidden; font-family: system-ui, sans-serif; }}
.viewport {{
  width: {width}px;
  height: {height}px;
  margin: 0 auto;
  cursor: grab;
  user-select: none;
  touch-action: none;
  text-align: center;
}}
.viewport.dragging {{ cursor: grabbing; }}
.stage {{
  width: 100%;
  height: {height - 32}px;
  perspective: 900px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.stage .photo-wrap {{
  max-width: 92%;
  max-height: 100%;
  transform-style: preserve-3d;
}}
.stage img {{
  width: 100%;
  height: 100%;
  max-height: {height - 52}px;
  border-radius: 14px;
  box-shadow: 0 14px 36px rgba(0,0,0,0.45);
  border: 1px solid rgba(139, 92, 246, 0.35);
  object-fit: cover;
  object-position: top center;
  transition: transform 0.1s ease-out, object-position 0.1s ease-out;
  transform-origin: center center;
}}
.meta {{
  margin-top: 8px;
  font-size: 0.72rem;
  color: #94a3b8;
}}
.deg {{
  display: inline-block;
  margin-top: 6px;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  color: #ddd6fe;
  background: rgba(139, 92, 246, 0.25);
}}
</style></head>
<body>
<div class="viewport" id="vp-{card_id}">
  <div class="stage"><div class="photo-wrap"><img id="img-{card_id}" alt="" draggable="false" /></div></div>
  <div class="deg" id="deg-{card_id}">0°</div>
  <div class="meta">← Drag to rotate · 360° →</div>
</div>
<script>
(function() {{
  const data = {data_json};
  const img = document.getElementById("img-{card_id}");
  const deg = document.getElementById("deg-{card_id}");
  const vp = document.getElementById("vp-{card_id}");
  if (!img || !deg || !vp) return;

  let idx = 0;
  let dragging = false;
  let lastX = 0;
  const pxPerStep = 5;

  const viewNames = {{ front: "Front", side: "Side", back: "Back", orbit: "" }};

  function applyFrame(f) {{
    img.src = f.url;
    img.style.objectPosition = "top center";
    let tf = "rotateY(0deg)";
    if (f.view === "side") {{
      if (f.styled) {{
        tf = "rotateY(62deg) scale(1.06)";
        img.style.objectPosition = "78% top";
      }} else {{
        tf = "rotateY(0deg)";
      }}
    }} else if (f.view === "back") {{
      if (f.styled || f.mirror) {{
        tf = "rotateY(0deg) scaleX(-1)";
      }}
    }}
    img.style.transform = tf;
  }}

  function show(i) {{
    const frames = data.frames || [];
    if (!frames.length) return;
    idx = ((i % frames.length) + frames.length) % frames.length;
    const f = frames[idx];
    applyFrame(f);
    const angle = Math.round((idx / frames.length) * 360);
    const vn = viewNames[f.view] || "";
    deg.textContent = vn ? angle + "° · " + vn : angle + "°";
  }}

  show(0);

  function onDown(x) {{
    dragging = true;
    lastX = x;
    vp.classList.add("dragging");
  }}
  function onMove(x) {{
    if (!dragging) return;
    const dx = x - lastX;
    if (Math.abs(dx) < pxPerStep) return;
    const steps = Math.trunc(dx / pxPerStep);
    lastX = x;
    show(idx - steps);
  }}
  function onUp() {{
    dragging = false;
    vp.classList.remove("dragging");
  }}

  vp.addEventListener("mousedown", (e) => {{ onDown(e.clientX); e.preventDefault(); }});
  window.addEventListener("mousemove", (e) => onMove(e.clientX));
  window.addEventListener("mouseup", onUp);
  vp.addEventListener("touchstart", (e) => {{
    if (e.touches.length) onDown(e.touches[0].clientX);
  }}, {{ passive: true }});
  vp.addEventListener("touchmove", (e) => {{
    if (e.touches.length) onMove(e.touches[0].clientX);
  }}, {{ passive: true }});
  vp.addEventListener("touchend", onUp);
}})();
</script>
</body></html>"""

    components.html(doc, height=height + 8, scrolling=False)


def render_image_3d(
    src: ImageSource,
    *,
    width: int | str = 200,
    height: int | None = None,
    key: str = "ft3d",
) -> None:
    """Interactive perspective card — photos appear 3D with mouse tilt."""
    import streamlit.components.v1 as components

    img_url = _image_url(src)
    safe_src = html.escape(img_url, quote=True)
    card_id = re.sub(r"[^a-zA-Z0-9_-]", "", key) or "ft3d"

    if height is None:
        height = int(width * 1.35) + 28 if isinstance(width, int) else 400

    w_style = f"{width}px" if isinstance(width, int) else str(width)
    cid = json.dumps(card_id)

    doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: transparent; overflow: hidden; }}
.scene {{
  width: {w_style};
  height: {height}px;
  margin: 0 auto;
  perspective: 1000px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.card {{
  position: relative;
  width: 94%;
  height: 96%;
  transform-style: preserve-3d;
  transition: transform 0.14s ease-out;
  transform: rotateY(-12deg) rotateX(4deg);
  border-radius: 14px;
  box-shadow:
    -16px 20px 40px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(139, 92, 246, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}}
.card img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  border-radius: 14px;
  display: block;
}}
.shine {{
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: linear-gradient(
    125deg,
    rgba(255, 255, 255, 0.28) 0%,
    transparent 42%,
    rgba(139, 92, 246, 0.15) 100%
  );
  pointer-events: none;
}}
.glow {{
  position: absolute;
  bottom: -6%;
  left: 8%;
  width: 84%;
  height: 14%;
  background: radial-gradient(ellipse, rgba(139, 92, 246, 0.45), transparent 72%);
  filter: blur(6px);
  pointer-events: none;
}}
</style></head>
<body>
<div class="scene" id="scene-{card_id}">
  <div class="card" id="{card_id}">
    <img src="{safe_src}" alt="" />
    <div class="shine"></div>
    <div class="glow"></div>
  </div>
</div>
<script>
(function() {{
  const card = document.getElementById({cid});
  const scene = document.getElementById("scene-{card_id}");
  if (!card || !scene) return;
  const base = {{ ry: -12, rx: 4 }};
  const apply = (x, y) => {{
    card.style.transform =
      "rotateY(" + (base.ry + x * 30) + "deg) rotateX(" + (base.rx - y * 24) +
      "deg) scale3d(1.04, 1.04, 1.04)";
  }};
  const reset = () => {{
    card.style.transform =
      "rotateY(" + base.ry + "deg) rotateX(" + base.rx + "deg) scale3d(1, 1, 1)";
  }};
  scene.addEventListener("mousemove", (e) => {{
    const r = scene.getBoundingClientRect();
    apply((e.clientX - r.left) / r.width - 0.5, (e.clientY - r.top) / r.height - 0.5);
  }});
  scene.addEventListener("mouseleave", reset);
  scene.addEventListener("touchmove", (e) => {{
    if (!e.touches.length) return;
    const r = scene.getBoundingClientRect();
    const t = e.touches[0];
    apply((t.clientX - r.left) / r.width - 0.5, (t.clientY - r.top) / r.height - 0.5);
  }}, {{ passive: true }});
  scene.addEventListener("touchend", reset);
}})();
</script>
</body></html>"""

    components.html(doc, height=height + 8, scrolling=False)
