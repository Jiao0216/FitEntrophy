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
    BODY_TYPE_LABELS,
    generate_mannequin_asset,
    model_image_for_tryon,
    model_image_source_label,
    resolve_display_source,
)
from fitentropy.outfit_agent import reduce_entropy
from fitentropy.ui_theme import (
    BODY_TYPE_EN,
    GENDER_EN,
    OCCASION_EN,
    WARDROBE_ICON,
    inject_theme,
    missing_items_html,
    render_footer,
    render_hero,
    render_nav,
    render_step_rail,
)

PAGE_TITLE = "FitEntropy"
SLOGAN = (
    "Every morning, your closet is in a state of maximum entropy. FitEntropy fixes that."
)

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_theme()
render_nav("dashboard")
render_hero(SLOGAN)

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

_active_step = 3 if "last_result" in st.session_state else 2
_rail_col, _main_col = st.columns([0.14, 0.86])
with _rail_col:
    render_step_rail(_active_step)
with _main_col:
    st.markdown(
        '<div class="ft-section"><p class="ft-section-head"><em>01</em> 你是谁 · Profile</p>',
        unsafe_allow_html=True,
    )
    g1, g2 = st.columns(2)
    with g1:
        gender = st.radio(
            "Gender · 性别",
            config.GENDER_OPTIONS,
            horizontal=True,
            key="ft_gender",
            format_func=lambda x: f"{GENDER_EN.get(x, x)} · {x}",
        )
    with g2:
        if "ft_body_type" not in st.session_state:
            st.session_state["ft_body_type"] = "标准"
        body_type = st.radio(
            "Body · 体型",
            list(BODY_TYPE_LABELS),
            horizontal=True,
            key="ft_body_type",
            format_func=lambda x: f"{BODY_TYPE_EN.get(x, (x, ''))[0]} · {x}",
        )
    st.caption(model_image_source_label(gender, body_type))
if fashn_configured():
    _gen_col1, _gen_col2 = st.columns(2)
    with _gen_col1:
        if st.button(
            "FASHN 生成当前模特",
            key="btn_fashn_gen_current",
            use_container_width=True,
            help="调用 FASHN model-create，约 1–2 分钟",
        ):
            st.session_state["fashn_gen_target"] = (gender, body_type)
    with _gen_col2:
        if st.button(
            "生成全部 6 套",
            key="btn_fashn_gen_all",
            use_container_width=True,
        ):
            st.session_state["fashn_gen_target"] = ("__all__", "")
else:
    st.caption("配置 FASHN_API_KEY 后可一键生成 AI 模特图。")
if st.session_state.get("fashn_gen_error"):
    st.error(st.session_state["fashn_gen_error"])
if st.session_state.get("fashn_gen_ok"):
    st.success(st.session_state["fashn_gen_ok"])

_gen_target = st.session_state.pop("fashn_gen_target", None)
if _gen_target and fashn_configured():
    st.session_state.pop("fashn_gen_error", None)
    st.session_state.pop("fashn_gen_ok", None)
    try:
        with st.spinner("FASHN model-create 生成中（约 1–2 分钟/张）…"):
            if _gen_target[0] == "__all__":
                from fitentropy.mannequin_assets import all_presets

                for g, b in all_presets():
                    generate_mannequin_asset(g, b, force=True)
                st.session_state["fashn_gen_ok"] = "已生成全部 6 套 FASHN 模特图。"
            else:
                g, b = _gen_target
                generate_mannequin_asset(g, b, force=True)
                st.session_state["fashn_gen_ok"] = f"已生成 {g} · {b} 的 FASHN 模特图。"
    except Exception as exc:
        st.session_state["fashn_gen_error"] = str(exc)
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

with st.form("entropy_form"):
    st.markdown(
        '<div class="ft-section"><p class="ft-section-head"><em>02</em> 你有什么 · Wardrobe</p>',
        unsafe_allow_html=True,
    )
    wardrobe_picks: dict[str, list[str]] = {}
    w1, w2 = st.columns(2)
    with w1:
        st.markdown(f"**{WARDROBE_ICON['上衣']} 上衣 · Tops**")
        wardrobe_picks["上衣"] = st.multiselect(
            "上衣",
            options=list(config.OWNED_WARDROBE["上衣"]),
            default=[],
            label_visibility="collapsed",
            placeholder="T恤、衬衫…",
        )
        st.markdown(f"**{WARDROBE_ICON['连衣裙']} 连衣裙 · Dresses**")
        wardrobe_picks["连衣裙"] = st.multiselect(
            "连衣裙",
            options=list(config.OWNED_WARDROBE["连衣裙"]),
            default=[],
            label_visibility="collapsed",
            placeholder="休闲裙、正式裙…",
        )
    with w2:
        st.markdown(f"**{WARDROBE_ICON['下装']} 下装 · Bottoms**")
        wardrobe_picks["下装"] = st.multiselect(
            "下装",
            options=list(config.OWNED_WARDROBE["下装"]),
            default=[],
            label_visibility="collapsed",
            placeholder="牛仔裤、休闲裤…",
        )
        st.markdown(f"**{WARDROBE_ICON['鞋子']} 鞋子 · Shoes**")
        wardrobe_picks["鞋子"] = st.multiselect(
            "鞋子",
            options=list(config.OWNED_WARDROBE["鞋子"]),
            default=[],
            label_visibility="collapsed",
            placeholder="运动鞋、靴子…",
        )
    c1, c2 = st.columns(2)
    with c1:
        occasion = st.selectbox(
            "Occasion · 场合",
            config.OCCASION_OPTIONS,
            format_func=lambda x: f"{OCCASION_EN.get(x, x)} · {x}",
        )
    with c2:
        budget = st.radio("Budget · 预算", config.BUDGET_OPTIONS, horizontal=True)

    with st.expander(
        "虚拟试穿（FASHN）",
        expanded=fashn_configured(),
    ):
        if fashn_configured():
            st.caption("已配置 FASHN · 模特按第 1 步性别/体型自动匹配；填商品图 URL 后勾选试穿。")
        else:
            st.caption("在 .env 设置 FASHN_API_KEY 后刷新页面即可启用。")
        fashn_garment_url = st.text_input(
            "商品图 URL（garment_image）",
            value="",
            placeholder="https://…",
        )
        fashn_run = st.checkbox(
            "生成虚拟试穿效果图",
            value=fashn_configured(),
            disabled=not fashn_configured(),
        )
        if not fashn_configured():
            st.caption("未配置 FASHN_API_KEY 时仅展示搭配与购买链接。")

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
                _mb = body_type
                st.session_state["last_mannequin_gender"] = _mg
                st.session_state["last_mannequin_body"] = _mb
                style_signal = [f"体型:{_mb}"]
                payload = asyncio.run(
                    reduce_entropy(
                        demo_mode=demo_mode,
                        user_id=everos_user,
                        gender=gender,
                        occasion=occasion,
                        owned_items=owned,
                        budget_tier=budget,
                        color_by_category={},
                        body_profile=None,
                        style_preferences=style_signal,
                    )
                )
                st.session_state.pop("fashn_tryon_urls", None)
                st.session_state.pop("fashn_tryon_error", None)
                if fashn_run and fashn_configured() and fashn_garment_url.strip():
                    try:
                        from fitentropy.fashn_client import run_tryon_v16

                        model_img, _src_label = model_image_for_tryon(_mg, _mb)
                        st.session_state["last_mannequin_label"] = _src_label
                        st.session_state["fashn_tryon_urls"] = run_tryon_v16(
                            model_img,
                            fashn_garment_url.strip(),
                        )
                    except Exception as exc:
                        st.session_state["fashn_tryon_error"] = str(exc)
            except Exception as exc:
                st.error(f"Pipeline failed: {exc}")
                st.stop()

        st.session_state["last_result"] = payload

if "last_result" in st.session_state:
    data = st.session_state["last_result"]
    trends = data.get("trend_keywords") or []
    outfits = data.get("outfits") or []
    notes = data.get("notes") or ""
    memory_snippet = data.get("memory_snippet") or ""
    actionbook_hints = data.get("actionbook_hints") or []

    _mg = st.session_state.get("last_mannequin_gender", st.session_state.get("ft_gender", "女"))
    _mb = st.session_state.get("last_mannequin_body", st.session_state.get("ft_body_type", "标准"))
    _tryon_urls = st.session_state.get("fashn_tryon_urls") or []
    _base_img = resolve_display_source(_mg, _mb)

    st.markdown(
        '<div class="ft-section"><p class="ft-section-head"><em>03</em> 结果展示 · Your Outfits</p></div>',
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

    _cols = st.columns(3)
    _occ = st.session_state.get("ft_last_occasion", "日常")
    for idx, outfit in enumerate(outfits[:3], start=1):
        title = outfit.get("title") or f"Look {idx}"
        desc = outfit.get("description") or ""
        missing = outfit.get("missing_labels") or []
        offers = outfit.get("offers") or []
        tag = missing[0] if missing else _occ
        img_src = _tryon_urls[(idx - 1) % len(_tryon_urls)] if _tryon_urls else _base_img
        card_body = missing_items_html(offers, missing)
        with _cols[idx - 1]:
            st.image(img_src, use_container_width=True)
            st.markdown(
                f"""<div class="ft-outfit-body">
  <div class="ft-outfit-num">{idx:02d}</div>
  <div class="ft-outfit-title">{html.escape(title)}</div>
  <span class="ft-tag">{html.escape(str(tag)[:24])}</span>
  <p class="ft-outfit-desc">{html.escape(desc)}</p>
  {card_body}
</div>""",
                unsafe_allow_html=True,
            )

    _owned_n = len(st.session_state.get("ft_last_owned") or [])
    render_footer(
        confidence=72.0 + min(20, len(outfits) * 4) + min(8, _owned_n),
        wardrobe_count=max(_owned_n, 1),
        outfit_count=max(len(outfits), 1) * 280,
    )
else:
    render_footer(confidence=78.6, wardrobe_count=0, outfit_count=842)
