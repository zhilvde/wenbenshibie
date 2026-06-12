"""Web 文本分析系统 — JetBrains 风格 · 中文界面"""
from __future__ import annotations

import json
from collections import Counter

import pandas as pd
import streamlit as st
from streamlit_echarts import st_pyecharts

from core import (
    fetch_page,
    cut_words, get_text_stats,
    extract_keywords_tfidf, extract_keywords_textrank,
    get_pos_distribution, get_ngrams, compare_counters,
    extract_html_tables,
    create_chart, create_comparison_chart, create_cooccurrence_graph,
)
from storage import save as save_history, load as load_history, remove as remove_history
from storage import counter_to_csv, html_report as build_html_report

# ================================================================
#  页面配置
# ================================================================
st.set_page_config(
    page_title="Web 文本分析",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
#  CSS 
# ================================================================
st.markdown("""
<style>
.stApp { background: #1e1f22; }
h1, h2, h3, h4, h5, h6, p, span, div, label, li {
    color: #ced0d6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
}
h2 { font-size: 1.1rem; font-weight: 600; color: #a8adbd; margin: 0 0 10px; }
h3 { font-size: 0.95rem; font-weight: 600; color: #a8adbd; }
h4 { font-size: 0.88rem; font-weight: 600; color: #9b9da4; }

[data-testid="stSidebar"] {
    background: #2b2d30;
    border-right: 1px solid #393b40;
}
[data-testid="stSidebar"] label { color: #a8adbd !important; font-size: 0.8rem; font-weight: 500; }
[data-testid="stSidebar"] hr { border-color: #393b40; margin: 14px 0; }
[data-testid="stSidebar"] .stSlider p { color: #7a7e87; font-size: 0.76rem; }

.stTextInput > div > div > input {
    border-radius: 4px !important;
    border: 1px solid #393b40 !important;
    padding: 7px 12px !important;
    font-size: 0.86rem !important;
    background: #2b2d30 !important;
    color: #ced0d6 !important;
    font-family: "JetBrains Mono","Cascadia Code","Fira Code","Consolas","Microsoft YaHei",monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3574f0 !important;
    box-shadow: 0 0 0 2px rgba(53,116,240,.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #5a5e66 !important; }

.stButton > button {
    background: #3574f0 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 7px 20px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    transition: background .15s !important;
}
.stButton > button:hover { background: #4d89f5 !important; }
.stButton > button:active { background: #2b5fc2 !important; }

.stDownloadButton > button {
    background: #2b2d30 !important;
    color: #ced0d6 !important;
    border: 1px solid #393b40 !important;
    border-radius: 4px !important;
    padding: 6px 14px !important;
    font-size: 0.8rem !important;
    transition: all .15s !important;
}
/* Metric Cards */
.metric-card {
    background: #2b2d30;
    border: 1px solid #393b40;
    border-radius: 4px;
    padding: 14px 12px;
    text-align: center;
    height: 100%;
    transition: border-color .15s;
}
.metric-card:hover { border-color: #4d5158; }
.metric-card.accent { border-left: 3px solid #3574f0; }
.mc-label {
    color: #7a7e87;
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-bottom: 4px;
}
.mc-value { color: #ced0d6; font-size: 1.4rem; font-weight: 600; }

[data-testid="stDataFrame"] {
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #393b40;
}
[data-testid="stDataFrame"] table { font-size: 0.8rem; }
[data-testid="stDataFrame"] th {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border-color: #393b40 !important;
}
[data-testid="stDataFrame"] td { border-color: #393b40 !important; color: #ced0d6 !important; }

.stTextArea textarea {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border: 1px solid #393b40 !important;
    border-radius: 4px !important;
    font-family: "JetBrains Mono","Cascadia Code","Fira Code","Consolas","Microsoft YaHei",monospace !important;
    font-size: 0.8rem !important;
}
.stAlert { border-radius: 4px !important; border: 1px solid #393b40 !important; background: #2b2d30 !important; }
.stSpinner > div { border-top-color: #3574f0 !important; }

.app-title { font-size: 1.35rem; font-weight: 600; color: #ced0d6; margin-bottom: 2px; }
.app-subtitle { font-size: 0.8rem; color: #7a7e87; margin-bottom: 18px; }
.source-bar { font-size: 0.83rem; color: #7a7e87; padding: 6px 0 2px; }
.source-bar a { color: #6B8EFF; text-decoration: none; }
.source-bar a:hover { text-decoration: underline; color: #8fa7ff; }
.empty-state { text-align: center; padding: 60px 20px; }
.empty-state .et { font-size: 0.95rem; color: #7a7e87; margin-bottom: 4px; }
.empty-state .ed { font-size: 0.8rem; color: #5a5e66; }

/* 欢迎页 */
.welcome-title { font-size: 1.6rem; font-weight: 700; color: #ced0d6; margin-bottom: 6px; }
.welcome-desc { font-size: 0.86rem; color: #7a7e87; margin-bottom: 32px; line-height: 1.7; }
.feat-card { background: #2b2d30; border: 1px solid #393b40; border-radius: 4px; padding: 16px 18px; height: 100%; }
.feat-card .fc-title { font-size: 0.82rem; font-weight: 600; color: #a8adbd; margin-bottom: 4px; }
.feat-card .fc-desc { font-size: 0.76rem; color: #7a7e87; line-height: 1.6; }
.flow-box { background: #2b2d30; border: 1px solid #393b40; border-radius: 4px; padding: 20px 24px; margin-top: 8px; }
.flow-box .fl-title { font-size: 0.82rem; font-weight: 600; color: #a8adbd; margin-bottom: 14px; }
.flow-box .fl-step-num { font-size: 1rem; font-weight: 700; color: #3574f0; margin-bottom: 2px; }
.flow-box .fl-step-label { font-size: 0.8rem; color: #a8adbd; margin-bottom: 2px; }
.flow-box .fl-step-desc { font-size: 0.72rem; color: #7a7e87; }

/* ---- 标签页（radio 驱动，隐藏圆点 + 下划线风格） ---- */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0;
    border-bottom: 1px solid #393b40;
    padding-bottom: 0;
    margin-bottom: 14px;
}
/* 隐藏 radio 输入圆圈 */
div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
div[data-testid="stRadio"] label {
    padding: 8px 16px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #7a7e87 !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    margin-bottom: -1px !important;
    transition: color .15s, border-color .15s !important;
    cursor: pointer !important;
}
div[data-testid="stRadio"] label:hover {
    color: #a8adbd !important;
}
div[data-testid="stRadio"] label[data-selected="true"] {
    color: #3574f0 !important;
    border-bottom-color: #3574f0 !important;
}

.chart-info {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 8px 14px;
    background: #2b2d30;
    border: 1px solid #393b40;
    border-radius: 4px;
    margin-bottom: 14px;
    font-size: 0.82rem;
}
.ci-item {
    color: #a8adbd;
    padding: 0 10px;
}
.ci-label {
    color: #7a7e87;
    font-size: 0.73rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 4px;
}
.ci-sep {
    width: 1px;
    height: 18px;
    background: #393b40;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
#  Session State 初始化
# ================================================================
DEFAULTS = {
    "analyzed": False,
    "url": "", "page_title": "", "text": "", "counter": None,
    "stats": None, "html_tables": [],
    "keywords_tfidf": [], "keywords_textrank": [],
    "pos_data": None, "ngrams": [], "csv_data": "",
    # 对比模式
    "url_b": "", "analyzed_b": False,
    "title_b": "", "text_b": "", "counter_b": None, "comparison": None,
    # 导出
    "html_report_data": "",
    "html_report_ready": False,
    "active_tab": "概览",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
#  数据预计算（在侧边栏之前，确保导出的 csv_data 可用）
# ================================================================
if st.session_state.analyzed and st.session_state.counter:
    _filtered = Counter(
        {k: v for k, v in st.session_state.counter.items() if v >= 2}
    )
    _csv = counter_to_csv(_filtered)
    # 只在发生变化时更新，避免不必要的 rerun
    st.session_state.csv_data = _csv

# ================================================================
#  侧边栏
# ================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:2px 0 14px;">
        <div style="font-size:1.05rem;font-weight:600;color:#ced0d6;">文本分析工具</div>
        <div style="font-size:0.73rem;color:#5a5e66;">Web Content Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:0.7rem;font-weight:600;color:#7a7e87;'
        'letter-spacing:.05em;text-transform:uppercase;margin-bottom:4px;">'
        '过滤</div>', unsafe_allow_html=True,
    )
    min_freq = st.slider("最低词频", 1, 20, 2, help="过滤出现次数低于此值的词语")

    st.markdown(
        '<div style="font-size:0.7rem;font-weight:600;color:#7a7e87;'
        'letter-spacing:.05em;text-transform:uppercase;margin:16px 0 4px;">'
        '图表</div>', unsafe_allow_html=True,
    )
    chart_type = st.selectbox(
        "图表类型",
        ["词云", "柱状图", "折线图", "饼图", "漏斗图", "散点图",
         "雷达图", "树图", "箱线图（词频分布）"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div style="font-size:0.7rem;font-weight:600;color:#7a7e87;'
        'letter-spacing:.05em;text-transform:uppercase;margin:16px 0 4px;">'
        '导出</div>', unsafe_allow_html=True,
    )

    safe_name = ""
    if st.session_state.analyzed:
        safe_name = st.session_state.page_title[:30].replace("/", "_").replace("\\", "_")

    # -- CSV 导出（始终可见，数据已预计算） --
    if st.session_state.analyzed and st.session_state.csv_data:
        st.download_button(
            "导出 CSV", data=st.session_state.csv_data,
            file_name=f"词频分析_{safe_name}.csv",
            mime="text/csv", use_container_width=True,
        )

    # -- HTML 报告生成 --
    if st.session_state.analyzed:
        if st.button("生成 HTML 报告", use_container_width=True,
                     key="gen_html_btn"):
            with st.spinner("正在生成报告..."):
                _f = Counter({k: v for k, v in st.session_state.counter.items()
                              if v >= min_freq})
                _c = create_chart(chart_type, _f.most_common(20))
                _r = build_html_report(
                    st.session_state.page_title, st.session_state.url,
                    st.session_state.stats, _c, _f.most_common(20),
                    st.session_state.keywords_tfidf,
                    st.session_state.ngrams,
                )
                st.session_state.html_report_data = _r
                st.session_state.html_report_ready = True
                st.rerun()

        # HTML 报告下载按钮（报告生成后持久可见）
        if st.session_state.html_report_ready and st.session_state.html_report_data:
            st.download_button(
                "下载 HTML 报告", data=st.session_state.html_report_data,
                file_name=f"分析报告_{safe_name}.html",
                mime="text/html", use_container_width=True,
            )
            if st.button("清除报告缓存", key="clear_html"):
                st.session_state.html_report_data = ""
                st.session_state.html_report_ready = False
                st.rerun()

    if st.button("重置会话", key="reset_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("""
    <div style="padding:8px 0;font-size:0.68rem;color:#5a5e66;line-height:1.7;">
    <p>1. 输入网页 URL<br>2. 点击「开始分析」<br>3. 切换标签页查看不同维度</p>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
#  主内容
# ================================================================
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

# ================================================================
#  分析逻辑
# ================================================================
if clicked and url:
    with st.spinner("正在抓取网页..."):
        try:
            title, text, soup = fetch_page(url)
        except ConnectionError as e:
            st.error(str(e))
            st.stop()
        except ValueError as e:
            st.warning(str(e))
            st.stop()

    with st.spinner("正在分词..."):
        counter = cut_words(text)
        stats = get_text_stats(text, counter)
        tables = extract_html_tables(soup)

    with st.spinner("正在提取关键词..."):
        kw_tf = extract_keywords_tfidf(text, 20)
        kw_tr = extract_keywords_textrank(text, 20)
        pos = get_pos_distribution(text)
        ng = get_ngrams(text, n=2, topK=20)

    # 保存历史
    try:
        save_history(url, title, counter, kw_tf)
    except Exception:
        pass

    st.session_state.update({
        "analyzed": True, "url": url, "page_title": title,
        "text": text, "counter": counter, "stats": stats,
        "html_tables": tables,
        "keywords_tfidf": kw_tf, "keywords_textrank": kw_tr,
        "pos_data": pos, "ngrams": ng,
        "analyzed_b": False, "comparison": None,
    })
    st.rerun()

# ================================================================
#  结果展示
# ================================================================
if st.session_state.analyzed and st.session_state.counter:
    counter = st.session_state.counter
    filtered = Counter({k: v for k, v in counter.items() if v >= min_freq})
    top20 = filtered.most_common(20)
    chart = create_chart(chart_type, top20)
    st.session_state.csv_data = counter_to_csv(filtered)

    st.markdown(
        f'<div class="source-bar">'
        f'来源：<a href="{st.session_state.url}" target="_blank">'
        f'{st.session_state.page_title}</a></div>',
        unsafe_allow_html=True,
    )

    # ---- 标签页导航（radio 驱动状态，CSS 隐藏圆点 + 下划线标签样式） ----
    TAB_NAMES = ["概览", "深度分析", "图表", "对比分析", "历史记录"]
    active = st.session_state.active_tab

    # 隐藏的 radio 驱动状态，上层 CSS 美化
    active = st.radio(
        "tabnav", TAB_NAMES,
        index=TAB_NAMES.index(active) if active in TAB_NAMES else 0,
        horizontal=True, label_visibility="collapsed",
    )
    if active != st.session_state.active_tab:
        st.session_state.active_tab = active
        st.rerun()

    # 根据活跃 Tab 条件渲染内容（只渲染当前 Tab，图表不被隐藏 iframe 问题）
    if active == "概览":
        s = st.session_state.stats
        cols = st.columns(5)
        metrics = [
            ("总字符数", s["总字符数（含空格换行）"]),
            ("有效词数", s["有效词语数"]),
            ("唯一词数", s["唯一词语数"]),
            ("句子数", s["句子数"]),
            ("段落数", s["段落数"]),
        ]
        for i, (label, val) in enumerate(metrics):
            with cols[i]:
                st.markdown(
                    f'<div class="metric-card{" accent" if i==1 else ""}">'
                    f'<div class="mc-label">{label}</div>'
                    f'<div class="mc-value">{val:,}</div></div>',
                    unsafe_allow_html=True,
                )

        cols2 = st.columns(3)
        sec = [
            ("有效字符数", s["有效字符数（去空格换行）"]),
            ("平均词长", s["平均词长"]),
            ("词频集中度", f"{s['唯一词语数'] / max(1, s['有效词语数']) * 100:.1f}%"),
        ]
        for i, (label, val) in enumerate(sec):
            with cols2[i]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="mc-label">{label}</div>'
                    f'<div class="mc-value">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 关键词（TF-IDF）")
            if st.session_state.keywords_tfidf:
                kw_df = pd.DataFrame(st.session_state.keywords_tfidf, columns=["词语", "权重"])
                kw_df["权重"] = kw_df["权重"].round(4)
                st.dataframe(kw_df, use_container_width=True, hide_index=True, height=310)
            else:
                st.caption("暂无关键词数据")
        with c2:
            st.markdown("#### 高频短语（2-gram）")
            if st.session_state.ngrams:
                ng_df = pd.DataFrame(st.session_state.ngrams[:15], columns=["短语", "频次"])
                st.dataframe(ng_df, use_container_width=True, hide_index=True, height=310)
            else:
                st.caption("暂无短语数据")

    elif active == "深度分析":
        ca, cb = st.columns(2)
        with ca:
            st.markdown("#### TF-IDF 关键词")
            if st.session_state.keywords_tfidf:
                df = pd.DataFrame(st.session_state.keywords_tfidf, columns=["词语", "权重"])
                df["权重"] = df["权重"].round(4)
                df.index = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True, height=320)
            else:
                st.caption("—")
        with cb:
            st.markdown("#### TextRank 关键词")
            if st.session_state.keywords_textrank:
                df = pd.DataFrame(st.session_state.keywords_textrank, columns=["词语", "权重"])
                df["权重"] = df["权重"].round(4)
                df.index = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True, height=320)
            else:
                st.caption("—")

        st.markdown("---")
        cc, cd = st.columns(2)
        with cc:
            st.markdown("#### 词性分布")
            pos = st.session_state.pos_data
            if pos and pos.get("categories"):
                df = pd.DataFrame(pos["categories"].items(), columns=["词性", "数量"])
                df = df.sort_values("数量", ascending=False)
                df.index = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True, height=240)
                if pos.get("entities"):
                    st.markdown("")
                    for etype, elist in pos["entities"].items():
                        if elist:
                            st.markdown(f"**{etype}**：" + "、".join(w for w, _ in elist[:8]))
            else:
                st.caption("词性数据不可用")
        with cd:
            st.markdown("#### 高频短语（2-gram）")
            if st.session_state.ngrams:
                df = pd.DataFrame(st.session_state.ngrams, columns=["短语", "频次"])
                df.index = range(1, len(df) + 1)
                st.dataframe(df, use_container_width=True, height=240)
            else:
                st.caption("—")

        st.markdown("---")
        st.markdown("#### 词共现网络图")
        try:
            graph = create_cooccurrence_graph(filtered)
            st_pyecharts(graph, height="500px")
        except Exception:
            st.caption("数据不足，无法生成网络图")

    elif active == "图表":
        st.markdown(
            f'<div class="chart-info">'
            f'<span class="ci-item"><span class="ci-label">图表</span> {chart_type}</span>'
            f'<span class="ci-sep"></span>'
            f'<span class="ci-item"><span class="ci-label">数据点</span> {len(top20)}</span>'
            f'<span class="ci-sep"></span>'
            f'<span class="ci-item"><span class="ci-label">最低词频</span> {min_freq}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if top20:
            st_pyecharts(chart, height="620px")
        else:
            st.info("当前过滤条件下无词频数据，请在侧边栏降低最低词频")
        st.caption("在侧边栏切换图表类型以查看不同可视化效果")

        if st.session_state.html_tables:
            st.markdown("---")
            st.markdown("#### 网页中的表格")
            for i, tbl in enumerate(st.session_state.html_tables):
                st.markdown(f"**{tbl['caption']}**")
                if tbl["rows"] and tbl["headers"]:
                    df = pd.DataFrame(tbl["rows"], columns=tbl["headers"])
                    st.dataframe(df, use_container_width=True, height=220)
                elif tbl["rows"]:
                    st.dataframe(pd.DataFrame(tbl["rows"]), use_container_width=True, height=220)

    elif active == "对比分析":
        st.markdown("#### 双 URL 对比分析")
        st.caption("输入第二个 URL，与当前文章进行词频差异分析")

        cu, cgo = st.columns([5, 1], gap="small")
        with cu:
            url_b = st.text_input(
                "第二个 URL", placeholder="https://example.com/another",
                label_visibility="collapsed", key="url_b_input",
            )
        with cgo:
            cmp_clicked = st.button("对比", use_container_width=True)

        if cmp_clicked and url_b:
            with st.spinner("正在抓取第二个网页..."):
                try:
                    ttl_b, txt_b, _ = fetch_page(url_b)
                except ConnectionError as e:
                    st.error(str(e))
                    st.stop()
                except ValueError as e:
                    st.warning(str(e))
                    st.stop()

            with st.spinner("正在分析对比..."):
                cnt_b = cut_words(txt_b)
                comp = compare_counters(counter, cnt_b)

                st.session_state.url_b = url_b
                st.session_state.title_b = ttl_b
                st.session_state.text_b = txt_b
                st.session_state.counter_b = cnt_b
                st.session_state.comparison = comp
                st.session_state.analyzed_b = True
                st.rerun()

        if st.session_state.analyzed_b and st.session_state.comparison:
            comp = st.session_state.comparison
            st.markdown("##### 对比摘要")
            cols = st.columns(4)
            for i, (label, val) in enumerate([
                ("两篇共有词", comp["shared"]),
                ("仅 A 有", comp["only_1_count"]),
                ("仅 B 有", comp["only_2_count"]),
                ("B 总词数", comp["total_2"]),
            ]):
                with cols[i]:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="mc-label">{label}</div>'
                        f'<div class="mc-value">{val:,}</div></div>',
                        unsafe_allow_html=True,
                    )

            cs, co = st.columns(2)
            with cs:
                st.markdown("##### 两篇共有高频词")
                if comp["top_shared"]:
                    df = pd.DataFrame(comp["top_shared"], columns=["词语", "总词频"])
                    st.dataframe(df, use_container_width=True, hide_index=True, height=280)
            with co:
                st.markdown("##### 仅当前文章 (A) 出现")
                if comp["top_only_1"]:
                    df = pd.DataFrame(comp["top_only_1"], columns=["词语", "词频"])
                    st.dataframe(df, use_container_width=True, hide_index=True, height=280)
                else:
                    st.caption("无独有词")

            st.markdown("---")
            st.markdown("##### 词频对比图")
            cmp_chart = create_comparison_chart(
                [(w, dict(comp["top_shared"]).get(w, 0)) for w, _ in comp["top_shared"][:15]],
                [(w, dict(comp["top_only_2"]).get(w, 0)) for w, _ in comp["top_only_2"][:15]],
                title=f"「{st.session_state.page_title[:20]}」vs「{st.session_state.title_b[:20]}」",
            )
            st_pyecharts(cmp_chart, height="450px")

            with st.expander("查看两篇原文"):
                x1, x2 = st.columns(2)
                with x1:
                    st.markdown(
                        f'<b style="color:#7a7e87;">A：</b>'
                        f'<span style="color:#ced0d6;">{st.session_state.page_title}</span>',
                        unsafe_allow_html=True,
                    )
                    st.text_area("A", value=st.session_state.text[:1500], height=280,
                                 disabled=True, label_visibility="collapsed")
                with x2:
                    st.markdown(
                        f'<b style="color:#7a7e87;">B：</b>'
                        f'<span style="color:#ced0d6;">{st.session_state.title_b}</span>',
                        unsafe_allow_html=True,
                    )
                    st.text_area("B", value=st.session_state.text_b[:1500], height=280,
                                 disabled=True, label_visibility="collapsed")

    elif active == "历史记录":
        st.markdown("#### 分析历史")
        try:
            history = load_history(30)
        except Exception:
            history = []

        if history:
            for rec in history:
                top_words_str = ""
                try:
                    top = json.loads(rec.get("top_words", "[]"))
                    top_words_str = "、".join(f"{w}({c})" for w, c in top[:6])
                except (json.JSONDecodeError, TypeError):
                    pass

                with st.expander(f"{rec['title'][:50]}  —  {rec['created_at']}"):
                    st.markdown(
                        f'<span style="color:#7a7e87;">URL：</span>'
                        f'<a href="{rec["url"]}" target="_blank" '
                        f'style="color:#6B8EFF;text-decoration:none;">'
                        f'{rec["url"][:60]}</a>'
                        f' &nbsp;|&nbsp; <b>总词数：</b>{rec["total_words"]}'
                        f' &nbsp;|&nbsp; <b>唯一词：</b>{rec["unique_words"]}',
                        unsafe_allow_html=True,
                    )
                    if top_words_str:
                        st.markdown(
                            f'<b style="color:#7a7e87;">高频词：</b>'
                            f'<span style="color:#a8adbd;">{top_words_str}</span>',
                            unsafe_allow_html=True,
                        )
                    if st.button("删除此记录", key=f"del_{rec['id']}"):
                        try:
                            remove_history(rec["id"])
                            st.rerun()
                        except Exception:
                            st.error("删除失败")
            st.caption(f"共 {len(history)} 条记录")
        else:
            st.markdown("""
            <div class="empty-state">
                <p class="et">暂无分析记录</p>
                <p class="ed">分析任意 URL 后将自动保存到此处</p>
            </div>
            """, unsafe_allow_html=True)

else:
        st.markdown(
            '<div class="welcome-desc" style="margin-top:8px;">'
            '输入任意中文网页 URL，自动完成抓取、分词、统计分析及多维可视化。'
            '适合内容运营者分析竞品文章，也适合研究者快速了解文本特征。</div>',
            unsafe_allow_html=True,
        )

        # 功能卡片 2x2
        cards = [
            ("数据抓取与解析", "自动请求网页、检测编码、提取正文与 HTML 表格，支持反爬回退策略。"),
            ("中文分词与统计", "jieba 分词 + TF-IDF / TextRank 关键词提取，词性标注、命名实体识别、N-gram 短语发现。"),
            ("多维图表可视化", "词云、柱状图、饼图、雷达图、树图等 9 种图表，词共现网络图、双 URL 对比图。"),
            ("报告导出与历史", "一键导出 CSV / HTML 分析报告，分析记录自动保存至本地，随时回看。"),
        ]
        for row in (cards[:2], cards[2:]):
            cols = st.columns(2, gap="medium")
            for i, (title, desc) in enumerate(row):
                with cols[i]:
                    st.markdown(
                        f'<div class="feat-card">'
                        f'<div class="fc-title">{title}</div>'
                        f'<div class="fc-desc">{desc}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("")

        # 使用流程
        flow = (
            '<div class="flow-box">'
            '<div class="fl-title">使用流程</div>'
            '<div style="display:flex;gap:16px;">'
        )
        for num, t, d in [
            ("01", "输入 URL", "粘贴中文网页链接"),
            ("02", "点击分析", "自动抓取与分词"),
            ("03", "切换标签页", "多维度浏览结果"),
            ("04", "导出报告", "CSV / HTML 离线报告"),
        ]:
            flow += (
                f'<div style="flex:1;">'
                f'<div class="fl-step-num">{num}</div>'
                f'<div class="fl-step-label">{t}</div>'
                f'<div class="fl-step-desc">{d}</div>'
                f'</div>'
            )
        flow += '</div></div>'
        st.markdown(flow, unsafe_allow_html=True)
