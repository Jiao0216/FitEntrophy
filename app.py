"""FitEntropy Streamlit shell."""

from __future__ import annotations

import asyncio
import html
import os

os.environ.setdefault("AGENTFIELD_LOG_LEVEL", "ERROR")
# Streamlit 退出时 Click 可能写 bytes；AgentField stdout tee 只接受 str，会导致进程被 kill 时出现 TypeError / exit 1
os.environ.setdefault("AGENTFIELD_LOGS_ENABLED", "false")

import streamlit as st

from fitentropy import config
from fitentropy.fashn_client import fashn_configured
from fitentropy.mannequin_assets import (
    file_to_data_uri,
    resolve_display_source,
)
from fitentropy.tryon_service import auto_tryon_for_outfits
from fitentropy.outfit_agent import reduce_entropy
from fitentropy.ui_theme import (
    OCCASION_EN,
    WARDROBE_ICON,
    accessory_thumbs_html,
    inject_theme,
    render_hero,
    render_nav,
)

PAGE_TITLE = "FitEntropy"
SLOGAN = "Dress for the date. Win the date."

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
        value=True,
        help="关闭后使用真实 LLM 生成搭配；Bright Data 可选（有 Key 才爬趋势/商品页）",
    )
    st.divider()
    st.caption("Keys")
    _llm_ok = config.llm_configured()
    st.caption(
        f"LLM · {config.llm_provider_label()} / {config.llm_model_label()}: "
        f"{'✓' if _llm_ok else '—'}"
    )
    if not config.OPENAI_API_KEY:
        st.caption("OpenAI：在 .env 设置 OPENAI_API_KEY 后优先走 OpenAI")
    st.caption(f"Bright Data: {'✓' if config.brightdata_configured() else '—（可选）'}")
    st.caption(f"EverOS: {'✓' if config.EVEROS_API_KEY else '—'}")
    st.caption(f"FASHN 试穿: {'✓' if fashn_configured() else '—'}")
    everos_user = st.text_input(
        "EverOS User ID",
        value=config.EVEROS_USER_ID,
        label_visibility="visible",
    )
    if not demo_mode and not config.live_pipeline_ready():
        st.warning("关闭演示模式需要 OPENAI_API_KEY 或 QWEN_API_KEY（.env 保存后请刷新页面）。")
    elif not demo_mode and not config.brightdata_configured():
        st.info("未配置 Bright Data：仍可用 OpenAI 生成搭配，商品链接为 Zara/H&M/UNIQLO 搜索直达。")

# ── STEP: form ────────────────────────────────────────────────────────────────
if st.session_state["ft_step"] == "form":
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
            min_value=140,
            max_value=210,
            value=170,
            step=1,
            key="ft_height_cm",
        )
    with g3:
        st.number_input(
            "体重 · WEIGHT (kg)",
            min_value=35,
            max_value=150,
            value=60,
            step=1,
            key="ft_weight_kg",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("entropy_form"):
        st.markdown(
            '<div class="ft-section"><p class="ft-section-badge-head">'
            '<span class="ft-section-badge">02</span>选择单品 · Select Items</p>',
            unsafe_allow_html=True,
        )
        wardrobe_picks: dict[str, list[str]] = {}
        _tab_cats = [
            ("上衣", "Tops"),
            ("下装", "Bottoms"),
            ("连衣裙", "Dresses"),
            ("鞋子", "Shoes"),
            ("配饰", "Accessories"),
            ("外套", "Outerwear"),
        ]
        _tabs = st.tabs([f"{WARDROBE_ICON[c]} {c} · {en}" for c, en in _tab_cats])
        for _tab, (cat, _) in zip(_tabs, _tab_cats):
            with _tab:
                wardrobe_picks[cat] = st.multiselect(
                    cat,
                    options=list(config.OWNED_WARDROBE[cat]),
                    default=[],
                    label_visibility="collapsed",
                )
        st.multiselect(
            "风格标签 · Style",
            options=config.STYLE_PREFERENCE_OPTIONS,
            key="ft_styles",
            placeholder="极简、街头休闲、quiet luxury…",
        )
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
                min_value=100,
                max_value=10000,
                value=1500,
                step=100,
                key="ft_budget_yuan",
            )
        st.markdown("</div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Reduce Entropy →", type="primary", use_container_width=True)

    if submitted:
        if not demo_mode and not config.live_pipeline_ready():
            st.error("请配置 OPENAI_API_KEY 或 QWEN_API_KEY，或开启演示模式。")
        else:
            with st.spinner("Reducing closet entropy…"):
                try:
                    owned = config.flatten_owned_picks(wardrobe_picks)
                    st.session_state["ft_last_owned"] = owned
                    st.session_state["ft_last_occasion"] = occasion
                    _mg = gender
                    _mb = st.session_state.get("ft_body_type", "标准")
                    st.session_state["last_mannequin_gender"] = _mg
                    st.session_state["last_mannequin_body"] = _mb
                    style_signal = list(st.session_state.get("ft_styles", [])) + [f"体型:{_mb}"]
                    payload = asyncio.run(
                        reduce_entropy(
                            demo_mode=demo_mode,
                            user_id=everos_user,
                            gender=gender,
                            occasion=occasion,
                            owned_items=owned,
                            budget_tier=config.budget_yuan_to_tier(
                                st.session_state.get("ft_budget_yuan", 1500)
                            ),
                            color_by_category={"all": []},
                            body_profile={
                                "height_cm": st.session_state["ft_height_cm"],
                                "weight_kg": st.session_state["ft_weight_kg"],
                            },
                            style_preferences=style_signal,
                        )
                    )
                    st.session_state.pop("fashn_tryon_by_outfit", None)
                    st.session_state.pop("fashn_tryon_error", None)
                    outfits_list = payload.get("outfits") or []
                    if (
                        not demo_mode
                        and fashn_configured()
                        and config.brightdata_configured()
                        and outfits_list
                    ):
                        with st.spinner("FASHN 虚拟试穿（自动抓取商品图）…"):
                            try:
                                st.session_state["fashn_tryon_by_outfit"] = auto_tryon_for_outfits(
                                    _mg, _mb, outfits_list
                                )
                            except Exception as exc:
                                st.session_state["fashn_tryon_error"] = str(exc)
                except Exception as exc:
                    st.error(f"Pipeline failed: {exc}")
                    st.stop()

            st.session_state["last_result"] = payload
            st.session_state["ft_step"] = "result"
            st.rerun()


# ── STEP: result ──────────────────────────────────────────────────────────────
elif st.session_state["ft_step"] == "result":
    _back_col, _label_col = st.columns([0.25, 0.75])
    with _back_col:
        if st.button("← 返回修改", key="back_to_form"):
            st.session_state["ft_step"] = "form"
            st.rerun()
    with _label_col:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
            'color:#64748b;line-height:2.2;">step 3 of 3 · your outfits</div>',
            unsafe_allow_html=True,
        )

    data = st.session_state["last_result"]
    trends = data.get("trend_keywords") or []
    outfits = data.get("outfits") or []
    notes = data.get("notes") or ""
    memory_snippet = data.get("memory_snippet") or ""

    _mg = st.session_state.get("last_mannequin_gender", st.session_state.get("ft_gender", "女"))
    _mb = st.session_state.get("last_mannequin_body", st.session_state.get("ft_body_type", "标准"))
    _tryon_by_outfit = st.session_state.get("fashn_tryon_by_outfit") or {}
    _base_img = resolve_display_source(_mg, _mb)

    st.markdown(
        '<p class="ft-section-badge-head"><span class="ft-section-badge">03</span>'
        '搭配结果 · Your Outfits</p>',
        unsafe_allow_html=True,
    )
    if notes:
        st.info(notes)
    if st.session_state.get("fashn_tryon_error"):
        st.warning(f"FASHN：{st.session_state['fashn_tryon_error']}")

    with st.expander("Trend signals · 趋势与记忆", expanded=False):
        if trends:
            st.caption(" · ".join(trends[:10]))
        if memory_snippet:
            st.caption(memory_snippet)

    if not outfits:
        st.info("暂无搭配，请返回修改")
    else:
        # ── Hero model image (Look 01) ─────────────────────────────────────
        _hero_raw = _tryon_by_outfit.get(1) or _base_img
        _hero_src = file_to_data_uri(_hero_raw) if not isinstance(_hero_raw, str) else _hero_raw
        _hero_label = html.escape(f"Look 01 · {outfits[0].get('title', 'default')}")
        st.markdown(
            f'<div class="ft-hero-model">'
            f'<img src="{_hero_src}" style="width:100%;height:100%;object-fit:cover;display:block;">'
            f'<div class="ft-hero-model-label">{_hero_label}</div>'
            f'</div>'
            f'<p class="ft-hero-model-caption">FASHN 虚拟试穿 · 默认展示 Look 01</p>',
            unsafe_allow_html=True,
        )

        # ── Three look cards ───────────────────────────────────────────────
        _occ = st.session_state.get("ft_last_occasion", "日常")
        _cols = st.columns(3)
        for idx, outfit in enumerate(outfits[:3], start=1):
            title = outfit.get("title") or f"Look {idx}"
            desc = outfit.get("description") or ""
            missing = outfit.get("missing_labels") or []
            offers = outfit.get("offers") or []
            trend_rationale = outfit.get("trend_rationale") or ""
            tag = missing[0] if missing else _occ
            thumbs = accessory_thumbs_html(offers)
            with _cols[idx - 1]:
                st.markdown(
                    f"""<div class="ft-look-card">
  <div class="ft-look-head">
    <span class="ft-look-num-badge">{idx:02d}</span>
    <span class="ft-look-star">☆</span>
  </div>
  <div class="ft-look-title-row">
    <span class="ft-look-title">{html.escape(title)}</span>
    <span class="ft-look-tag">{html.escape(str(tag)[:24])}</span>
  </div>
  <p class="ft-look-desc">{html.escape(desc)}</p>
  <div class="ft-look-accessories-label">Accessories</div>
  {thumbs}
  <button class="ft-look-detail-btn">查看详情 →</button>
</div>""",
                    unsafe_allow_html=True,
                )
                with st.expander(f"Look {idx:02d} 详情", expanded=False):
                    if missing:
                        st.markdown("**Missing Items**")
                        for m in missing:
                            st.caption(f"• {m}")
                    if trend_rationale:
                        st.markdown("**Trend Rationale**")
                        st.caption(trend_rationale)


