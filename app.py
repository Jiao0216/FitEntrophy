"""FitEntropy Streamlit shell — simplified flow: gender/body/style/occasion/color → 3 outfits → try-on."""

from __future__ import annotations

import asyncio
import html
import os

os.environ.setdefault("AGENTFIELD_LOG_LEVEL", "ERROR")
os.environ.setdefault("AGENTFIELD_LOGS_ENABLED", "false")

import streamlit as st

from fitentropy import config
from fitentropy.fashn_client import fashn_configured
from fitentropy.mannequin_assets import (
    infer_body_type,
    resolve_display_source,
)
from fitentropy.tryon_service import auto_tryon_for_outfits
from fitentropy.outfit_agent import reduce_entropy
from fitentropy.ui_theme import (
    OCCASION_EN,
    WARDROBE_ICON,
    inject_theme,
    render_footer,
    render_hero,
    render_image_3d,
    render_nav,
)

PAGE_TITLE = "FitEntropy"
SLOGAN = "Dress for the date. Win the date."

# Color hex map for display
_COLOR_HEX = {
    "黑": "#000000", "白": "#f8fafc", "灰": "#6b7280", "米白": "#f5f0e8",
    "驼色": "#c4a882", "牛仔蓝": "#4a7eb5", "藏蓝": "#1e3a8a",
    "军绿": "#556b2f", "酒红": "#8b1a1a", "粉色": "#f9a8d4",
    "紫色": "#8b5cf6", "棕色": "#92400e", "银色": "#c0c0c0", "金色": "#d4a017",
}

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.session_state.setdefault("ft_step", "form")

inject_theme()
render_nav(active="Outfits" if st.session_state.get("ft_step") == "result" else "Dashboard")
render_hero(SLOGAN)

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    with st.expander("赛前清单 · 额度与部署", expanded=False):
        st.markdown(
            """
- [Bright Data](https://get.brightdata.com/aibuilders10)
- [Qwen Cloud](https://tinyurl.com/qwencloudcredits)
- [Qoder](https://tinyurl.com/qodercredits)
- Zeabur 当天：[BUILDER0516](https://zeabur.com/events?code=BUILDER0516)
            """
        )

    st.markdown("### 运行")
    demo_mode = st.toggle(
        "演示模式（Mock）",
        value=False,
        help="开启后使用 Mock 数据；关闭后调用真实 LLM 生成搭配",
    )
    st.divider()
    st.caption("Keys")
    _llm_ok = config.llm_configured()
    st.caption(
        f"LLM · {config.llm_provider_label()} / {config.llm_model_label()}: "
        f"{'✓' if _llm_ok else '—'}"
    )
    st.caption(f"Bright Data: {'✓' if config.brightdata_configured() else '—（可选）'}")
    st.caption(f"FASHN 试穿: {'✓' if fashn_configured() else '—'}")
    if not demo_mode and not config.live_pipeline_ready():
        st.warning("关闭演示模式需要 OPENAI_API_KEY 或 QWEN_API_KEY。")


# ══════════════════════════════════════════════════════════════════════════════
# STEP: form — 性别 + 体型 + 风格偏好 + 场合 + 颜色 + 预算
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["ft_step"] == "form":

    # ── 01 基础信息 ──
    st.markdown(
        '<div class="ft-section"><p class="ft-section-badge-head">'
        '<span class="ft-section-badge">01</span>基础信息 · Basic Info</p>',
        unsafe_allow_html=True,
    )
    g1, g2, g3 = st.columns(3)
    with g1:
        gender = st.radio(
            "性别 · GENDER",
            config.GENDER_OPTIONS,
            horizontal=True,
            key="ft_gender",
            format_func=lambda x: f"{'⚲' if x == '男' else '♀'} {x}",
        )
    with g2:
        st.number_input(
            "身高 · HEIGHT (cm)",
            min_value=140, max_value=210, value=170, step=1,
            key="ft_height_cm",
        )
    with g3:
        st.number_input(
            "体重 · WEIGHT (kg)",
            min_value=35, max_value=150, value=60, step=1,
            key="ft_weight_kg",
        )

    # BMI → Body type (internal only)
    _body_profile = {
        "height_cm": st.session_state.get("ft_height_cm", 170),
        "weight_kg": st.session_state.get("ft_weight_kg", 60),
    }
    _profile_b = infer_body_type(_body_profile, gender=st.session_state.get("ft_gender", gender))
    st.session_state["ft_body_type"] = _profile_b
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 02 偏好设置 ──
    with st.form("entropy_form"):
        st.markdown(
            '<div class="ft-section"><p class="ft-section-badge-head">'
            '<span class="ft-section-badge">02</span>偏好设置 · Preferences</p>',
            unsafe_allow_html=True,
        )

        # Category tabs — select which types to include in recommendation
        st.markdown(
            '<div style="font-size:0.72rem;color:#94a3b8;margin-bottom:0.35rem;'
            'letter-spacing:0.04em;">想买什么 · CATEGORIES</div>',
            unsafe_allow_html=True,
        )
        _cat_cols = st.columns(6)
        _cat_options = [
            ("上衣", "👕", "Tops"),
            ("下装", "👖", "Bottoms"),
            ("连衣裙", "👗", "Dresses"),
            ("鞋子", "👟", "Shoes"),
            ("配饰", "👜", "Accessories"),
            ("外套", "🧥", "Outerwear"),
        ]
        selected_cats = []
        for ci, (cat_cn, icon, cat_en) in enumerate(_cat_options):
            with _cat_cols[ci]:
                if st.checkbox(
                    f"{icon} {cat_cn}",
                    value=False,
                    key=f"ft_cat_{cat_cn}",
                    label_visibility="visible",
                ):
                    selected_cats.append(cat_cn)

        st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)

        # Style tags
        style_prefs = st.multiselect(
            "风格标签 · Style",
            options=config.STYLE_PREFERENCE_OPTIONS,
            key="ft_styles",
            placeholder="极简、街头休闲、quiet luxury…",
        )

        # Occasion + Budget
        c1, c2 = st.columns(2)
        with c1:
            occasion = st.selectbox(
                "Occasion · 场合",
                config.OCCASION_OPTIONS,
                format_func=lambda x: f"{OCCASION_EN.get(x, x)} · {x}",
            )
        with c2:
            st.number_input(
                "Budget · 预算 (¥)",
                min_value=100, max_value=10000, value=1500, step=100,
                key="ft_budget_yuan",
            )

        # Colors
        st.markdown(
            '<div style="font-size:0.72rem;color:#94a3b8;margin-bottom:0.35rem;'
            'letter-spacing:0.04em;">颜色偏好 · COLORS</div>',
            unsafe_allow_html=True,
        )
        selected_colors = st.multiselect(
            "颜色", options=list(config.COLOR_PREFERENCE_OPTIONS),
            default=[], label_visibility="collapsed",
            placeholder="选择偏好颜色…", key="ft_colors",
        )
        # Color circles display
        if selected_colors:
            color_chips = []
            for c in selected_colors:
                hex_c = _COLOR_HEX.get(c, "#6b7280")
                border = "1px solid #475569" if hex_c in ("#000000",) else "1px solid rgba(139,92,246,0.3)"
                color_chips.append(
                    f'<span style="display:flex;align-items:center;gap:6px;font-size:0.74rem;'
                    f'padding:0.28rem 0.6rem;border-radius:8px;border:1px solid #8b5cf6;'
                    f'background:rgba(139,92,246,0.18);color:#ddd6fe;">'
                    f'<span style="width:12px;height:12px;border-radius:50%;'
                    f'background:{hex_c};border:{border};"></span>'
                    f'{html.escape(c)}</span>'
                )
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:0.4rem;align-items:center;">'
                f'{"".join(color_chips)}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Reduce Entropy →", type="primary", use_container_width=True)

    if submitted:
        if not demo_mode and not config.live_pipeline_ready():
            st.error("请配置 OPENAI_API_KEY 或 QWEN_API_KEY，或开启演示模式。")
        else:
            with st.spinner("AI 搭配生成中…"):
                try:
                    _mg = gender
                    _mb = st.session_state.get("ft_body_type", "标准")
                    st.session_state["last_mannequin_gender"] = _mg
                    st.session_state["last_mannequin_body"] = _mb
                    st.session_state["ft_last_occasion"] = occasion

                    # Build style signal: body type + style prefs + categories + color + budget
                    style_signal = [f"体型:{_mb}"]
                    if style_prefs:
                        style_signal.extend([f"风格:{s}" for s in style_prefs])
                    if selected_cats:
                        style_signal.append(f"想买:{'、'.join(selected_cats)}")
                    if selected_colors:
                        style_signal.append(f"偏好色:{'、'.join(selected_colors)}")
                    budget_yuan = st.session_state.get("ft_budget_yuan", 1500)
                    style_signal.append(f"预算上限:{budget_yuan}¥")

                    # Color map for LLM: all categories share same color prefs
                    color_by_cat: dict[str, list[str]] = {}
                    if selected_colors:
                        for cat in config.OWNED_WARDROBE_ORDER:
                            color_by_cat[cat] = list(selected_colors)

                    # No wardrobe — recommend from scratch
                    owned: list[str] = []

                    payload = asyncio.run(
                        reduce_entropy(
                            demo_mode=demo_mode,
                            user_id=config.EVEROS_USER_ID,
                            gender=gender,
                            occasion=occasion,
                            owned_items=owned,
                            budget_tier=config.budget_yuan_to_tier(budget_yuan),
                            color_by_category=color_by_cat if selected_colors else None,
                            body_profile=_body_profile,
                            style_preferences=style_signal,
                        )
                    )
                    st.session_state.pop("fashn_tryon_by_outfit", None)
                    st.session_state.pop("fashn_tryon_error", None)
                    outfits_list = payload.get("outfits") or []
                    if demo_mode:
                        # Demo mode: use mock try-on results (gender-aware)
                        from fitentropy.mock_data import mock_tryon_results, mock_male_tryon_results
                        if _mg == "男":
                            st.session_state["fashn_tryon_by_outfit"] = mock_male_tryon_results()
                        else:
                            st.session_state["fashn_tryon_by_outfit"] = mock_tryon_results()
                    elif (
                        fashn_configured()
                        and outfits_list
                    ):
                        with st.spinner("FASHN 虚拟试穿中…"):
                            try:
                                st.session_state["fashn_tryon_by_outfit"] = auto_tryon_for_outfits(
                                    _mg, _mb, outfits_list
                                )
                            except Exception as exc:
                                st.session_state["fashn_tryon_error"] = str(exc)
                except Exception as exc:
                    st.error(f"生成失败: {exc}")
                    st.stop()

            st.session_state["last_result"] = payload
            st.session_state["ft_step"] = "result"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP: result — 试穿效果 + Shop Now
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state["ft_step"] == "result":
    _back_col, _label_col = st.columns([0.25, 0.75])
    with _back_col:
        if st.button("← 返回修改", key="back_to_form"):
            st.session_state["ft_step"] = "form"
            st.rerun()
    with _label_col:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
            'color:#64748b;line-height:2.2;">step 2 of 2 · your outfits</div>',
            unsafe_allow_html=True,
        )

    data = st.session_state.get("last_result")
    if not data:
        st.session_state["ft_step"] = "form"
        st.rerun()

    outfits = data.get("outfits") or []
    notes = data.get("notes") or ""

    _mg = st.session_state.get("last_mannequin_gender", "女")
    _mb = st.session_state.get("last_mannequin_body", "标准")
    _tryon_by_outfit = st.session_state.get("fashn_tryon_by_outfit") or {}
    _base_img = resolve_display_source(_mg, _mb)

    st.markdown(
        '<p class="ft-section-badge-head"><span class="ft-section-badge">03</span>'
        '搭配结果 · Your Outfits</p>',
        unsafe_allow_html=True,
    )

    # Show selected preferences as tags
    _user_styles = st.session_state.get("ft_styles", [])
    _user_occ = st.session_state.get("ft_last_occasion", "")
    _user_colors = st.session_state.get("ft_colors", [])
    _user_cats = [
        cat_cn for cat_cn, _icon, _cat_en in [
            ("上衣", "👕", "Tops"), ("下装", "👖", "Bottoms"), ("连衣裙", "👗", "Dresses"),
            ("鞋子", "👟", "Shoes"), ("配饰", "👜", "Accessories"), ("外套", "🧥", "Outerwear"),
        ]
        if st.session_state.get(f"ft_cat_{cat_cn}", False)
    ]
    _tags = []
    if _user_occ:
        _tags.append(f"{OCCASION_EN.get(_user_occ, _user_occ)} · {_user_occ}")
    for s in _user_styles:
        _tags.append(s)
    for c in _user_colors:
        _tags.append(c)
    for cat in _user_cats:
        _tags.append(cat)
    if _tags:
        _tag_html = " ".join(
            f'<span style="display:inline-block;font-size:0.68rem;padding:0.2rem 0.55rem;'
            f'border-radius:6px;border:1px solid rgba(139,92,246,0.3);'
            f'background:rgba(139,92,246,0.12);color:#c4b5fd;margin:0.15rem 0.2rem;">'
            f'{html.escape(t)}</span>'
            for t in _tags
        )
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:0.2rem;margin-bottom:0.75rem;">{_tag_html}</div>',
            unsafe_allow_html=True,
        )
    if notes:
        st.info(notes)
    if st.session_state.get("fashn_tryon_error"):
        st.warning(f"FASHN：{st.session_state['fashn_tryon_error']}")

    if not outfits:
        st.info("暂无搭配，请返回修改")
    else:
        # ── Hero model image (Look 01) ─────────────────────────────────────
        _look1_tryon = _tryon_by_outfit.get(1)
        _look1_title = outfits[0].get("title", "Look 01") if outfits else "Look 01"
        _hero_label = html.escape(f"Look 01 · {_look1_title}")
        _look1_offers = (outfits[0].get("offers") or []) if outfits else []

        _pl, _pc, _pr = st.columns([2, 1.5, 2])
        with _pc:
            if _look1_tryon and isinstance(_look1_tryon, dict) and _look1_tryon.get("tryon_url"):
                render_image_3d(
                    _look1_tryon["tryon_url"],
                    width=280, height=400,
                    key="hero-tryon-1",
                )
            else:
                render_image_3d(
                    _base_img,
                    width=280, height=400,
                    key="hero-mannequin",
                )
            st.markdown(
                f'<div style="text-align:center;font-size:0.7rem;color:#c4b5fd;'
                f'font-family:\'JetBrains Mono\',monospace;margin-top:0.25rem;">'
                f'{_hero_label}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="text-align:center;font-size:0.78rem;color:#64748b;">'
                'FASHN 虚拟试穿 · 默认展示 Look 01</div>',
                unsafe_allow_html=True,
            )

            # Generate try-on button if no try-on yet
            if (not _look1_tryon or not (isinstance(_look1_tryon, dict) and _look1_tryon.get("tryon_url"))) and fashn_configured() and outfits:
                if st.button("✨ 生成试穿效果", key="gen_tryon_btn", use_container_width=True):
                    with st.spinner("正在生成试穿效果…"):
                        try:
                            st.session_state["fashn_tryon_by_outfit"] = auto_tryon_for_outfits(
                                _mg, _mb, outfits
                            )
                        except Exception as exc:
                            st.session_state["fashn_tryon_error"] = str(exc)
                    st.rerun()

        # ── Product thumbnails for Look 01 (garment + shoes + accessories) ──
        with _pl:
            pass  # spacing
        with _pr:
            st.markdown(
                '<div style="font-size:0.72rem;color:#94a3b8;margin-bottom:0.35rem;'
                'letter-spacing:0.04em;">搭配单品 · ITEMS</div>',
                unsafe_allow_html=True,
            )
            for off in _look1_offers:
                if not isinstance(off, dict):
                    continue
                prod = off.get("product") or {}
                _pimg = (prod.get("image_url") or "").strip()
                _pname = str(prod.get("name") or off.get("label") or "").strip()
                _pprice = str(prod.get("price_display") or "").strip()
                _purl = (prod.get("url") or "").strip()
                _pbrand = str(prod.get("brand") or "").strip()
                if _pimg:
                    _c1, _c2 = st.columns([1, 2.5])
                    with _c1:
                        render_image_3d(_pimg, width=64, height=64, key=f"hero-prod-{_pname[:10]}")
                    with _c2:
                        st.markdown(
                            f'<div style="font-size:0.74rem;color:#e2e8f0;font-weight:600;">'
                            f'{html.escape(_pname[:28])}</div>'
                            f'<div style="font-size:0.66rem;color:#94a3b8;">'
                            f'{html.escape(_pbrand)} · {html.escape(_pprice)}</div>',
                            unsafe_allow_html=True,
                        )
                        if _purl.startswith("http"):
                            st.link_button(
                                "购买 →",
                                _purl,
                                key=f"hero-buy-{_pname[:10]}",
                            )

    render_footer()
