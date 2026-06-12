"""Web 文本分析系统 — 入口"""
from __future__ import annotations

from collections import Counter

import streamlit as st

from ui.styles import inject as inject_css
from ui.sidebar import render as render_sidebar
from ui.tabs import run_analysis, render_results
from ui.welcome import render as render_welcome
from storage import counter_to_csv

# ---- 页面配置 ----
st.set_page_config(
    page_title="Web 文本分析",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- CSS ----
inject_css(st)

# ---- Session State ----
DEFAULTS = {
    "analyzed": False,
    "url": "", "page_title": "", "text": "", "counter": None,
    "stats": None, "html_tables": [],
    "keywords_tfidf": [], "keywords_textrank": [],
    "pos_data": None, "ngrams": [], "csv_data": "",
    "url_b": "", "analyzed_b": False,
    "title_b": "", "text_b": "", "counter_b": None, "comparison": None,
    "html_report_data": "", "html_report_ready": False,
    "active_tab": "概览",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---- csv 预计算 ----
if st.session_state.analyzed and st.session_state.counter:
    _filtered = Counter({k: v for k, v in st.session_state.counter.items() if v >= 2})
    st.session_state.csv_data = counter_to_csv(_filtered)

# ---- 侧边栏 ----
with st.sidebar:
    min_freq, chart_type = render_sidebar(
        st.session_state.counter,
        st.session_state.page_title,
        st.session_state.stats,
        st.session_state.keywords_tfidf,
        st.session_state.ngrams,
    )

# ---- 主内容 ----
st.markdown('<div class="app-title">Web 文本分析系统</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">输入 URL，自动抓取网页并完成分词、统计与多维可视化</div>',
    unsafe_allow_html=True,
)

col_u, col_b = st.columns([5, 1], gap="small")
with col_u:
    url = st.text_input("文章 URL", placeholder="https://example.com/article",
                        label_visibility="collapsed", key="url_input")
with col_b:
    clicked = st.button("开始分析", use_container_width=True)

# ---- 分析 ----
if clicked and url:
    run_analysis(url)

# ---- 结果 / 欢迎页 ----
if st.session_state.analyzed and st.session_state.counter:
    render_results(min_freq, chart_type)
else:
    render_welcome()
