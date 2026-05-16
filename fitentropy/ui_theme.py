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
    radial-gradient(ellipse 40% 30% at 100% 0%, rgba(59, 130, 246, 0.12), transparent);
  color: #e2e8f0;
}
.block-container { padding-top: 0.5rem; max-width: 1280px; }
[data-testid="stSidebar"] {
  background: #0c0a14 !important;
  border-right: 1px solid rgba(139, 92, 246, 0.15) !important;
}
.ft-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 0 1.25rem; border-bottom: 1px solid rgba(139, 92, 246, 0.12);
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
.ft-nav-links { display: flex; gap: 1.5rem; }
.ft-nav-links a {
  color: #94a3b8; text-decoration: none; font-size: 0.88rem; font-weight: 500;
}
.ft-nav-links a.active { color: #c4b5fd; border-bottom: 2px solid #8b5cf6; padding-bottom: 2px; }
.ft-hero-title {
  text-align: center; font-size: 1.35rem; font-weight: 600; color: #f1f5f9;
  max-width: 42rem; margin: 0 auto 1.25rem; line-height: 1.45;
}
.ft-terminal {
  background: rgba(12, 10, 20, 0.95); border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 12px; padding: 1rem; font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; line-height: 1.65; color: #a78bfa;
}
.ft-terminal .ok { color: #4ade80; }
.ft-entropy-panel {
  background: rgba(12, 10, 20, 0.85); border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 12px; padding: 1rem; text-align: center;
}
.ft-entropy-panel .formula {
  font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #c4b5fd;
}
.ft-mesh {
  height: 100px; margin: 0.5rem 0;
  background: radial-gradient(circle at 50% 50%, rgba(139,92,246,0.35), transparent 70%);
  border-radius: 8px;
}
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
.ft-footer {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 1rem; padding: 1rem 0 2rem; border-top: 1px solid rgba(139, 92, 246, 0.12);
  font-size: 0.78rem; color: #64748b;
}
.ft-footer-mono { font-family: 'JetBrains Mono', monospace; color: #94a3b8; }
.ft-confidence-bar {
  width: 120px; height: 6px; background: rgba(139, 92, 246, 0.2);
  border-radius: 99px; overflow: hidden; display: inline-block; vertical-align: middle;
}
.ft-confidence-fill {
  height: 100%; background: linear-gradient(90deg, #7c3aed, #a78bfa); border-radius: 99px;
}
.stFormSubmitButton > button {
  width: 100% !important; padding: 0.75rem !important; border-radius: 12px !important;
  background: linear-gradient(135deg, #6d28d9, #8b5cf6, #a78bfa) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 0 24px rgba(139, 92, 246, 0.4) !important;
}
label, [data-testid="stWidgetLabel"] p { color: #e2e8f0 !important; }
[data-baseweb="select"] > div {
  background: rgba(15, 12, 24, 0.9) !important;
  border-color: rgba(139, 92, 246, 0.25) !important; border-radius: 10px !important;
}
motion[data-testid="stImage"] img {
  border-radius: 16px 16px 0 0 !important; border: 1px solid rgba(139, 92, 246, 0.2) !important;
}
""".replace("motion[data-testid", "div[data-testid")

BODY_TYPE_EN = {"高挑": ("Tall / Slim", "↗"), "标准": ("Standard", "◎"), "丰满": ("Fuller", "●")}
GENDER_EN = {"男": "Male", "女": "Female"}
WARDROBE_ICON = {"上衣": "👕", "下装": "👖", "连衣裙": "👗", "鞋子": "👟"}
OCCASION_EN = {"日常": "Daily", "通勤": "Work", "约会": "Date", "派对": "Party"}


def inject_theme() -> None:
    import streamlit as st

    st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)


def render_nav(active: str = "dashboard") -> None:
    import streamlit as st

    links = [
        ("dashboard", "Dashboard"),
        ("wardrobe", "Wardrobe"),
        ("outfits", "Outfits"),
        ("profile", "Profile"),
    ]
    link_html = "".join(
        f'<a class="{"active" if k == active else ""}">{html.escape(label)}</a>'
        for k, label in links
    )
    st.markdown(
        f'<header class="ft-nav"><motion class="ft-logo"><motion class="ft-logo-icon">F</motion>'
        f'<span class="ft-logo-text">FitEntropy</span></motion>'
        f'<nav class="ft-nav-links">{link_html}</nav></header>'.replace("<motion", "<div").replace(
            "</motion>", "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_hero(slogan: str) -> None:
    import streamlit as st

    st.markdown(f'<p class="ft-hero-title">{html.escape(slogan)}</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """<div class="ft-terminal"><span class="ok">$</span> initializing FitEntropy…<br>
<span class="ok">$</span> loading wardrobe graph… OK<br>
<span class="ok">$</span> fetching trend signals… OK<br>
<span class="ok">$</span> reducing entropy…</motion>""".replace("</motion>", "</div>"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """<div class="ft-entropy-panel"><div class="ft-mesh"></div>
<div class="formula">entropy = − Σ p(i) · log p(i)</div>
<div style="font-size:0.75rem;color:#64748b;margin-top:0.35rem;">style_confidence → max</div></div>""",
            unsafe_allow_html=True,
        )


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
    import streamlit as st

    pct = min(99.0, max(0.0, confidence))
    st.markdown(
        f"""<footer class="ft-footer">
  <span>FitEntropy AI Engine v1.0.0 · Style Confidence
    <span class="ft-confidence-bar"><span class="ft-confidence-fill" style="width:{pct:.1f}%"></span></span>
    {pct:.1f}%
  </span>
  <span class="ft-footer-mono">git commit -m "Fix entropy, look great"</span>
  <span>wardrobe_items: {wardrobe_count} · outfit_options: {outfit_count}</span>
</footer>""",
        unsafe_allow_html=True,
    )


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
