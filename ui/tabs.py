"""标签页 —— 概览 / 深度分析 / 图表 / 对比分析 / 历史记录"""
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
from storage import counter_to_csv

TAB_NAMES = ["概览", "深度分析", "图表", "对比分析", "历史记录"]


# ================================================================
#  分析执行
# ================================================================

def run_analysis(url: str) -> None:
    """执行完整分析流程，结果写入 st.session_state。"""
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
#  结果渲染
# ================================================================

def render_results(min_freq: int, chart_type: str) -> None:
    """渲染分析结果：Tab 导航 + 5 个 Tab 内容。"""
    counter: Counter = st.session_state.counter
    filtered = Counter({k: v for k, v in counter.items() if v >= min_freq})
    top20 = filtered.most_common(20)
    chart = create_chart(chart_type, top20)
    st.session_state.csv_data = counter_to_csv(filtered)

    # 来源链接
    st.markdown(
        f'<div class="source-bar">'
        f'来源：<a href="{st.session_state.url}" target="_blank">'
        f'{st.session_state.page_title}</a></div>',
        unsafe_allow_html=True,
    )

    # Tab 导航
    active = st.session_state.get("active_tab", "概览")
    active = st.radio(
        "tabnav", TAB_NAMES,
        index=TAB_NAMES.index(active) if active in TAB_NAMES else 0,
        horizontal=True, label_visibility="collapsed",
    )
    if active != st.session_state.active_tab:
        st.session_state.active_tab = active
        st.rerun()

    # 条件渲染
    if active == "概览":
        _render_overview()
    elif active == "深度分析":
        _render_deep(filtered)
    elif active == "图表":
        _render_charts(chart_type, top20, chart, min_freq, filtered, counter)
    elif active == "对比分析":
        _render_compare(counter)
    elif active == "历史记录":
        _render_history()


# ================================================================
#  概览
# ================================================================

def _render_overview() -> None:
    s = st.session_state.stats
    cols = st.columns(5)
    for i, (label, val) in enumerate([
        ("总字符数", s["总字符数（含空格换行）"]),
        ("有效词数", s["有效词语数"]),
        ("唯一词数", s["唯一词语数"]),
        ("句子数", s["句子数"]),
        ("段落数", s["段落数"]),
    ]):
        with cols[i]:
            st.markdown(
                f'<div class="metric-card{" accent" if i == 1 else ""}">'
                f'<div class="mc-label">{label}</div>'
                f'<div class="mc-value">{val:,}</div></div>',
                unsafe_allow_html=True,
            )

    cols2 = st.columns(3)
    for i, (label, val) in enumerate([
        ("有效字符数", s["有效字符数（去空格换行）"]),
        ("平均词长", s["平均词长"]),
        ("词频集中度", f"{s['唯一词语数'] / max(1, s['有效词语数']) * 100:.1f}%"),
    ]):
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
        kw = st.session_state.keywords_tfidf
        if kw:
            df = pd.DataFrame(kw, columns=["词语", "权重"])
            df["权重"] = df["权重"].round(4)
            st.dataframe(df, use_container_width=True, hide_index=True, height=310)
        else:
            st.caption("暂无关键词数据")
    with c2:
        st.markdown("#### 高频短语（2-gram）")
        ng = st.session_state.ngrams
        if ng:
            df = pd.DataFrame(ng[:15], columns=["短语", "频次"])
            st.dataframe(df, use_container_width=True, hide_index=True, height=310)
        else:
            st.caption("暂无短语数据")


# ================================================================
#  深度分析
# ================================================================

def _render_deep(filtered: Counter) -> None:
    ca, cb = st.columns(2)
    with ca:
        st.markdown("#### TF-IDF 关键词")
        kw = st.session_state.keywords_tfidf
        if kw:
            df = pd.DataFrame(kw, columns=["词语", "权重"])
            df["权重"] = df["权重"].round(4)
            df.index = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True, height=320)
        else:
            st.caption("—")
    with cb:
        st.markdown("#### TextRank 关键词")
        tr = st.session_state.keywords_textrank
        if tr:
            df = pd.DataFrame(tr, columns=["词语", "权重"])
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
        ng = st.session_state.ngrams
        if ng:
            df = pd.DataFrame(ng, columns=["短语", "频次"])
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


# ================================================================
#  图表
# ================================================================

def _render_charts(
    chart_type: str, top20: list, chart,
    min_freq: int, filtered: Counter, counter: Counter,
) -> None:
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
        for tbl in st.session_state.html_tables:
            st.markdown(f"**{tbl['caption']}**")
            if tbl["rows"] and tbl["headers"]:
                df = pd.DataFrame(tbl["rows"], columns=tbl["headers"])
                st.dataframe(df, use_container_width=True, height=220)
            elif tbl["rows"]:
                st.dataframe(pd.DataFrame(tbl["rows"]), use_container_width=True, height=220)


# ================================================================
#  对比分析
# ================================================================

def _render_compare(counter: Counter) -> None:
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


# ================================================================
#  历史记录
# ================================================================

def _render_history() -> None:
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
