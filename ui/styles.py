"""JetBrains New UI 风格 CSS"""
from __future__ import annotations

import streamlit as st

CSS = """
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

.welcome-desc { font-size: 0.86rem; color: #7a7e87; margin-bottom: 32px; line-height: 1.7; }
.feat-card { background: #2b2d30; border: 1px solid #393b40; border-radius: 4px; padding: 16px 18px; height: 100%; }
.feat-card .fc-title { font-size: 0.82rem; font-weight: 600; color: #a8adbd; margin-bottom: 4px; }
.feat-card .fc-desc { font-size: 0.76rem; color: #7a7e87; line-height: 1.6; }
.flow-box { background: #2b2d30; border: 1px solid #393b40; border-radius: 4px; padding: 20px 24px; margin-top: 8px; }
.flow-box .fl-title { font-size: 0.82rem; font-weight: 600; color: #a8adbd; margin-bottom: 14px; }
.flow-box .fl-step-num { font-size: 1rem; font-weight: 700; color: #3574f0; margin-bottom: 2px; }
.flow-box .fl-step-label { font-size: 0.8rem; color: #a8adbd; margin-bottom: 2px; }
.flow-box .fl-step-desc { font-size: 0.72rem; color: #7a7e87; }

div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0;
    border-bottom: 1px solid #393b40;
    padding-bottom: 0;
    margin-bottom: 14px;
}
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
div[data-testid="stRadio"] label:hover { color: #a8adbd !important; }
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
.ci-item { color: #a8adbd; padding: 0 10px; }
.ci-label {
    color: #7a7e87;
    font-size: 0.73rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 4px;
}
.ci-sep { width: 1px; height: 18px; background: #393b40; flex-shrink: 0; }
</style>
"""


def inject(st_obj: st) -> None:
    """注入全局 CSS 样式。"""
    st_obj.markdown(CSS, unsafe_allow_html=True)
