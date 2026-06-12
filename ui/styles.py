"""JetBrains New UI 风格 CSS —— 含动画、Tab 滑动下划线、侧边栏卡片化"""
from __future__ import annotations

import streamlit as st

CSS = """
<style>
/* ================================================================
   Global
   ================================================================ */
.stApp { background: #1e1f22; }
h1, h2, h3, h4, h5, h6, p, span, div, label, li {
    color: #ced0d6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
}
h2 { font-size: 1.1rem; font-weight: 600; color: #a8adbd; margin: 0 0 10px; }
h3 { font-size: 0.95rem; font-weight: 600; color: #a8adbd; }
h4 { font-size: 0.88rem; font-weight: 600; color: #9b9da4; }

/* ---- 页面加载淡入 ---- */
.stApp { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0.5; } to { opacity: 1; } }

/* ---- 主内容区呼吸边距 ---- */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1200px;
}

/* ================================================================
   Sidebar
   ================================================================ */
[data-testid="stSidebar"] {
    background: #25272b;
    border-right: 1px solid #303236;
    padding-top: 0.5rem;
}
[data-testid="stSidebar"] label { color: #a8adbd !important; font-size: 0.8rem; font-weight: 500; }
[data-testid="stSidebar"] hr { border-color: #303236; margin: 10px 0; }
[data-testid="stSidebar"] .stSlider p { color: #7a7e87; font-size: 0.76rem; }

/* 侧边栏分组卡片 */
.sb-section {
    font-size: 0.68rem;
    font-weight: 600;
    color: #6b6f78;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 20px 0 6px;
    padding: 0 2px;
}
.sb-section:first-of-type { margin-top: 4px; }

/* 侧边栏分组容器 */
.sb-group {
    background: #2b2d30;
    border: 1px solid #303236;
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 4px;
    transition: border-color 0.2s;
}
.sb-group:hover { border-color: #3a3d44; }

/* ================================================================
   Input / Button
   ================================================================ */
.stTextInput > div > div > input {
    border-radius: 6px !important;
    border: 1px solid #393b40 !important;
    padding: 9px 14px !important;
    font-size: 0.88rem !important;
    background: #2b2d30 !important;
    color: #ced0d6 !important;
    font-family: "JetBrains Mono","Cascadia Code","Fira Code","Consolas","Microsoft YaHei",monospace !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3574f0 !important;
    box-shadow: 0 0 0 3px rgba(53,116,240,.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #5a5e66 !important; }

/* 主按钮（开始分析） */
.stButton > button {
    background: #3574f0 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 22px !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #4d89f5 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(53,116,240,.25) !important;
}
.stButton > button:active {
    background: #2b5fc2 !important;
    transform: translateY(0);
}

.stDownloadButton > button {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border: 1px solid #393b40 !important;
    border-radius: 6px !important;
    padding: 7px 14px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    border-color: #3574f0 !important;
    color: #ced0d6 !important;
    background: #32353a !important;
    transform: translateY(-1px);
}

/* 侧边栏按钮统一 */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stDownloadButton > button {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border: 1px solid #393b40 !important;
    border-radius: 6px !important;
    padding: 7px 14px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    border-color: #3574f0 !important;
    color: #ced0d6 !important;
    background: #32353a !important;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(53,116,240,.15) !important;
}

/* ================================================================
   Metric Cards（动画增强）
   ================================================================ */
.metric-card {
    background: #2b2d30;
    border: 1px solid #303236;
    border-radius: 6px;
    padding: 16px 14px;
    text-align: center;
    height: 100%;
    transition: all 0.25s ease;
    animation: cardIn 0.35s ease-out both;
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.metric-card:nth-child(2) { animation-delay: 0.04s; }
.metric-card:nth-child(3) { animation-delay: 0.08s; }
.metric-card:nth-child(4) { animation-delay: 0.12s; }
.metric-card:nth-child(5) { animation-delay: 0.16s; }
.metric-card:hover {
    border-color: #4d5158;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,.25);
}
.metric-card.accent {
    border-left: 3px solid #3574f0;
    background: linear-gradient(135deg, #2b2d30 0%, #2d3040 100%);
}
.mc-label {
    color: #7a7e87;
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.mc-value {
    color: #e8eaed;
    font-size: 1.5rem;
    font-weight: 600;
    transition: color 0.2s;
}
.metric-card:hover .mc-value { color: #fff; }

/* ================================================================
   Dataframe
   ================================================================ */
[data-testid="stDataFrame"] {
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #303236;
    transition: border-color 0.2s;
}
[data-testid="stDataFrame"]:hover { border-color: #3a3d44; }
[data-testid="stDataFrame"] table { font-size: 0.8rem; }
[data-testid="stDataFrame"] th {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border-color: #303236 !important;
}
[data-testid="stDataFrame"] td { border-color: #303236 !important; color: #ced0d6 !important; }

.stTextArea textarea {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border: 1px solid #303236 !important;
    border-radius: 6px !important;
    font-family: "JetBrains Mono","Cascadia Code","Fira Code","Consolas","Microsoft YaHei",monospace !important;
    font-size: 0.8rem !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus { border-color: #3574f0 !important; }
.stAlert { border-radius: 6px !important; border: 1px solid #303236 !important; background: #2b2d30 !important; }

/* ================================================================
   Spinner（脉冲动画）
   ================================================================ */
.stSpinner > div { border-top-color: #3574f0 !important; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
.stSpinner { animation: pulse 1.5s ease-in-out infinite; }

/* ================================================================
   Title / Source
   ================================================================ */
.app-title { font-size: 1.4rem; font-weight: 600; color: #ced0d6; margin-bottom: 2px; }
.app-subtitle { font-size: 0.8rem; color: #7a7e87; margin-bottom: 20px; }
.source-bar {
    font-size: 0.83rem; color: #7a7e87; padding: 6px 0 8px;
    border-bottom: 1px solid #25272c; margin-bottom: 4px;
}
.source-bar a { color: #6B8EFF; text-decoration: none; transition: color 0.15s; }
.source-bar a:hover { text-decoration: underline; color: #9db5ff; }

/* ================================================================
   Tab Navigation（radio 驱动，无圆点，滑动下划线）
   ================================================================ */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0;
    border-bottom: 1px solid #303236;
    padding-bottom: 0;
    margin-bottom: 16px;
    position: relative;
}
/* 彻底隐藏 radio 圆点 + 伪元素 */
div[data-testid="stRadio"] input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}
/* 隐藏 radio 的圆点指示器 */
div[data-testid="stRadio"] label::before,
div[data-testid="stRadio"] label::after {
    display: none !important;
}
div[data-testid="stRadio"] label {
    padding: 10px 18px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #6b6f78 !important;
    background: transparent !important;
    border-radius: 0 !important;
    margin-bottom: 0 !important;
    transition: color 0.2s ease !important;
    cursor: pointer !important;
    position: relative;
}
div[data-testid="stRadio"] label:hover {
    color: #a8adbd !important;
    background: rgba(53,116,240,.04) !important;
}
div[data-testid="stRadio"] label[data-selected="true"] {
    color: #3574f0 !important;
    background: transparent !important;
}
/* 滑动下划线（利用 label 自身的 border-bottom 过渡模拟） */
div[data-testid="stRadio"] label {
    border-bottom: 2px solid transparent !important;
    padding-bottom: 8px !important;
}
div[data-testid="stRadio"] label[data-selected="true"] {
    border-bottom-color: #3574f0 !important;
}

/* ================================================================
   Chart Info Bar
   ================================================================ */
.chart-info {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 10px 16px;
    background: #2b2d30;
    border: 1px solid #303236;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 0.82rem;
    animation: cardIn 0.3s ease-out;
}
.ci-item { color: #a8adbd; padding: 0 10px; }
.ci-label {
    color: #7a7e87;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 4px;
}
.ci-sep { width: 1px; height: 18px; background: #303236; flex-shrink: 0; }

/* ================================================================
   Welcome Page
   ================================================================ */
.welcome-desc { font-size: 0.88rem; color: #7a7e87; margin-bottom: 34px; line-height: 1.7; }
.feat-card {
    background: #2b2d30;
    border: 1px solid #303236;
    border-radius: 6px;
    padding: 18px 20px;
    height: 100%;
    transition: all 0.25s ease;
    animation: cardIn 0.35s ease-out both;
}
.feat-card:nth-child(1) { animation-delay: 0s; }
.feat-card:nth-child(2) { animation-delay: 0.06s; }
.feat-card:nth-child(3) { animation-delay: 0.12s; }
.feat-card:nth-child(4) { animation-delay: 0.18s; }
.feat-card:hover {
    border-color: #3574f0;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,.3);
}
.feat-card .fc-title { font-size: 0.84rem; font-weight: 600; color: #a8adbd; margin-bottom: 6px; }
.feat-card .fc-desc { font-size: 0.78rem; color: #7a7e87; line-height: 1.65; }

.flow-box {
    background: #2b2d30;
    border: 1px solid #303236;
    border-radius: 6px;
    padding: 22px 26px;
    margin-top: 8px;
    transition: border-color 0.2s;
    animation: cardIn 0.4s ease-out both;
    animation-delay: 0.24s;
}
.flow-box:hover { border-color: #3a3d44; }
.flow-box .fl-title { font-size: 0.84rem; font-weight: 600; color: #a8adbd; margin-bottom: 16px; }
.flow-box .fl-step-num {
    font-size: 1.05rem; font-weight: 700; color: #3574f0; margin-bottom: 4px;
    transition: transform 0.2s;
}
.flow-box > div > div:hover .fl-step-num { transform: scale(1.15); }
.flow-box .fl-step-label { font-size: 0.8rem; color: #a8adbd; margin-bottom: 2px; }
.flow-box .fl-step-desc { font-size: 0.73rem; color: #7a7e87; }

/* ================================================================
   Expander（历史记录）
   ================================================================ */
.stExpander > details {
    border: 1px solid #303236 !important;
    border-radius: 6px !important;
    background: #2b2d30 !important;
    margin-bottom: 6px !important;
    transition: border-color 0.2s !important;
}
.stExpander > details:hover { border-color: #3a3d44 !important; }
.stExpander > details[open] { border-color: #3574f0 !important; }

</style>
"""


def inject(st_obj: st) -> None:
    """注入全局 CSS 样式。"""
    st_obj.markdown(CSS, unsafe_allow_html=True)
