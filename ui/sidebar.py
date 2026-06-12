"""侧边栏 —— 过滤、图表选择、导出、重置"""
from __future__ import annotations

from collections import Counter

import streamlit as st

from core.charts import create_chart
from storage.export import counter_to_csv
from storage.export import html_report as build_html_report


def render(
    counter: Counter | None,
    page_title: str,
    stats: dict | None,
    keywords_tfidf: list,
    ngrams: list,
) -> tuple[int, str]:
    """
    渲染侧边栏。返回 (min_freq, chart_type) 供主流程使用。

    直接读写 st.session_state 中的导出、重置相关状态。
    """
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
    min_freq: int = st.slider("最低词频", 1, 20, 2, help="过滤出现次数低于此值的词语")

    st.markdown(
        '<div style="font-size:0.7rem;font-weight:600;color:#7a7e87;'
        'letter-spacing:.05em;text-transform:uppercase;margin:16px 0 4px;">'
        '图表</div>', unsafe_allow_html=True,
    )
    chart_type: str = st.selectbox(
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
    if st.session_state.get("analyzed"):
        safe_name = (page_title or "")[:30].replace("/", "_").replace("\\", "_")

    # CSV 导出
    csv_data = st.session_state.get("csv_data", "")
    if st.session_state.get("analyzed") and csv_data:
        st.download_button(
            "导出 CSV", data=csv_data,
            file_name=f"词频分析_{safe_name}.csv",
            mime="text/csv", use_container_width=True,
        )

    # HTML 报告
    if st.session_state.get("analyzed"):
        if st.button("生成 HTML 报告", use_container_width=True, key="gen_html_btn"):
            with st.spinner("正在生成报告..."):
                _f = Counter({k: v for k, v in (counter or {}).items() if v >= min_freq})
                _c = create_chart(chart_type, _f.most_common(20))
                _r = build_html_report(
                    page_title, st.session_state.get("url", ""),
                    stats or {}, _c, _f.most_common(20),
                    keywords_tfidf or [], ngrams or [],
                )
                st.session_state["html_report_data"] = _r
                st.session_state["html_report_ready"] = True
                st.rerun()

        if st.session_state.get("html_report_ready") and st.session_state.get("html_report_data"):
            st.download_button(
                "下载 HTML 报告",
                data=st.session_state["html_report_data"],
                file_name=f"分析报告_{safe_name}.html",
                mime="text/html", use_container_width=True,
            )
            if st.button("清除报告缓存", key="clear_html"):
                st.session_state["html_report_data"] = ""
                st.session_state["html_report_ready"] = False
                st.rerun()

    # 重置
    if st.button("重置会话", key="reset_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("""
    <div style="padding:8px 0;font-size:0.68rem;color:#5a5e66;line-height:1.7;">
    <p>1. 输入网页 URL<br>2. 点击「开始分析」<br>3. 切换标签页查看不同维度</p>
    </div>
    """, unsafe_allow_html=True)

    return min_freq, chart_type
