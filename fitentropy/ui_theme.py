"""FitEntropy dashboard theme (HTML + CSS helpers for Streamlit)."""

from __future__ import annotations

import html

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
[data-testid="stSidebar"] {
  background: #0c0a14 !important;
  border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
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
.ft-rail-wrap { border-left: 2px solid rgba(139, 92, 246, 0.35); padding-left: 1rem; }
.ft-rail-step { margin-bottom: 1.5rem; }
.ft-rail-num { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #8b5cf6; }
.ft-rail-title { font-size: 0.95rem; font-weight: 600; color: #f8fafc; }
.ft-rail-sub { font-size: 0.72rem; color: #64748b; text-transform: uppercase; }
.ft-rail-step.active .ft-rail-title { color: #c4b5fd; }
.ft-section {
  background: rgba(15, 12, 24, 0.75); border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 16px; padding: 1.35rem 1.5rem; margin-bottom: 1.25rem;
}
.ft-section-head { font-size: 1rem; font-weight: 600; color: #f8fafc; margin: 0 0 1rem; }
.ft-section-head em { color: #8b5cf6; font-style: normal; }
.ft-outfit-body { padding: 0.85rem 0 0; }
.ft-outfit-num { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #8b5cf6; }
.ft-outfit-title { font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin: 0.25rem 0; }
.ft-tag {
  display: inline-block; font-size: 0.68rem; padding: 0.2rem 0.5rem; border-radius: 6px;
  background: rgba(139, 92, 246, 0.25); color: #ddd6fe; margin-bottom: 0.4rem;
}
.ft-outfit-desc { font-size: 0.82rem; color: #94a3b8; line-height: 1.5; }
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
/* ── Section badge header ─────────────────────────────────────────────────── */
.ft-section-badge-head { font-size: 1rem; font-weight: 500; color: #f8fafc; margin: 0 0 1rem; }
.ft-section-badge {
  display: inline-block; width: 30px; height: 30px; border-radius: 8px;
  border: 1px solid rgba(139,92,246,0.35); color: #a78bfa;
  font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
  line-height: 30px; text-align: center;
  margin-right: 0.55rem; vertical-align: -7px;
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
motion[data-testid="stImage"] img {
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
""".replace("motion[data-testid", "div[data-testid")

BODY_TYPE_EN = {"高挑": ("Tall / Slim", "↗"), "标准": ("Standard", "◎"), "丰满": ("Fuller", "●")}
GENDER_EN = {"男": "Male", "女": "Female"}
WARDROBE_ICON = {"上衣": "👕", "下装": "👖", "连衣裙": "👗", "鞋子": "👟", "配饰": "👜", "外套": "🧥"}
OCCASION_EN = {"日常": "Daily", "通勤": "Work", "约会": "Date", "派对": "Party"}


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

    steps = [(1, "你是谁", "Who are you"), (2, "你有什么", "What do you have"), (3, "结果展示", "Your Outfits")]
    inner = []
    for num, zh, en in steps:
        cls = "ft-rail-step active" if num == active_step else "ft-rail-step"
        inner.append(
            f'<div class="{cls}"><div class="ft-rail-num">{num}</div>'
            f'<div class="ft-rail-title">{html.escape(zh)}</div>'
            f'<div class="ft-rail-sub">{html.escape(en)}</div></div>'
        )
    st.markdown(f'<div class="ft-rail-wrap">{"".join(inner)}</div>', unsafe_allow_html=True)


def render_footer(*, confidence: float, wardrobe_count: int, outfit_count: int) -> None:
    pass


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
