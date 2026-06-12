"""默认欢迎页"""
from __future__ import annotations

import streamlit as st


def render() -> None:
    """渲染未分析时的欢迎介绍页。"""
    st.markdown(
        '<div class="welcome-desc" style="margin-top:8px;">'
        '输入任意中文网页 URL，自动完成抓取、分词、统计分析及多维可视化。'
        '适合内容运营者分析竞品文章，也适合研究者快速了解文本特征。</div>',
        unsafe_allow_html=True,
    )

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
