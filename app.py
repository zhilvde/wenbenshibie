"""Web Text Analyzer — JetBrains New UI Style"""
import json
import streamlit as st
import pandas as pd
from collections import Counter
from streamlit_echarts import st_pyecharts
from utils import (
    fetch_page, cut_words, get_text_stats,
    extract_html_tables, create_chart,
    counter_to_csv, export_html_report,
    extract_keywords_tfidf, extract_keywords_textrank,
    get_pos_distribution, get_ngrams,
    compare_counters, create_comparison_chart, create_cooccurrence_graph,
    save_analysis, get_history, delete_history,
)

# ================================================================
#  Page Config
# ================================================================
st.set_page_config(
    page_title="Web Text Analyzer",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
#  JetBrains New UI — CSS
# ================================================================
st.markdown("""
<style>
/* ---- Global ---- */
.stApp {
    background: #1e1f22;
}
h1, h2, h3, h4, h5, h6, p, span, div, label, li {
    color: #ced0d6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
}
h2 { font-size: 1.15rem; font-weight: 600; color: #a8adbd; margin: 0 0 12px; }
h3 { font-size: 1rem; font-weight: 600; color: #a8adbd; margin: 0 0 8px; }
h4 { font-size: 0.92rem; font-weight: 600; color: #9b9da4; }
small, .caption { color: #7a7e87 !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #2b2d30;
    border-right: 1px solid #393b40;
}
[data-testid="stSidebar"] label {
    color: #a8adbd !important;
    font-size: 0.82rem;
    font-weight: 500;
}
[data-testid="stSidebar"] .stSlider p {
    color: #7a7e87;
    font-size: 0.78rem;
}
[data-testid="stSidebar"] hr {
    border-color: #393b40;
    margin: 16px 0;
}

/* ---- Input ---- */
.stTextInput > div > div > input {
    border-radius: 4px !important;
    border: 1px solid #393b40 !important;
    padding: 7px 12px !important;
    font-size: 0.88rem !important;
    background: #2b2d30 !important;
    color: #ced0d6 !important;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas",
                 "Microsoft YaHei", monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3574f0 !important;
    box-shadow: 0 0 0 2px rgba(53, 116, 240, 0.15) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #5a5e66 !important;
}

/* ---- Button ---- */
.stButton > button {
    background: #3574f0 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 7px 20px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background: #4d89f5 !important;
}
.stButton > button:active {
    background: #2b5fc2 !important;
}

/* ---- Secondary button ---- */
.stDownloadButton > button {
    background: #2b2d30 !important;
    color: #ced0d6 !important;
    border: 1px solid #393b40 !important;
    border-radius: 4px !important;
    padding: 6px 16px !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
    background: #32353a !important;
    border-color: #3574f0 !important;
}

/* ---- Tabs (underline style) ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #393b40;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0;
    padding: 8px 18px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #7a7e87;
    background: transparent;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    transition: color 0.15s, border-color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #a8adbd;
}
.stTabs [aria-selected="true"] {
    color: #3574f0 !important;
    border-bottom-color: #3574f0 !important;
    background: transparent !important;
}

/* ---- Metric cards ---- */
.metric-card {
    background: #2b2d30;
    border: 1px solid #393b40;
    border-radius: 4px;
    padding: 16px;
    text-align: center;
    height: 100%;
    transition: border-color 0.15s;
}
.metric-card:hover {
    border-color: #4d5158;
}
.metric-card .mc-label {
    color: #7a7e87;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}
.metric-card .mc-value {
    color: #ced0d6;
    font-size: 1.5rem;
    font-weight: 600;
}
.metric-card.accent {
    border-left: 3px solid #3574f0;
}

/* ---- Panel / Section ---- */
.section-panel {
    background: #2b2d30;
    border: 1px solid #393b40;
    border-radius: 4px;
    padding: 20px;
    margin-bottom: 16px;
}
.section-panel > :first-child {
    margin-top: 0;
}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #393b40;
}
[data-testid="stDataFrame"] table {
    font-size: 0.82rem;
}
[data-testid="stDataFrame"] th {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    font-weight: 600;
    border-color: #393b40 !important;
}
[data-testid="stDataFrame"] td {
    border-color: #393b40 !important;
    color: #ced0d6 !important;
}

/* ---- Text area ---- */
.stTextArea textarea {
    background: #2b2d30 !important;
    color: #a8adbd !important;
    border: 1px solid #393b40 !important;
    border-radius: 4px !important;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas",
                 "Microsoft YaHei", monospace !important;
    font-size: 0.82rem !important;
}

/* ---- Selectbox ---- */
.stSelectbox > div > div {
    background: #2b2d30 !important;
    border: 1px solid #393b40 !important;
    border-radius: 4px !important;
    color: #ced0d6 !important;
}

/* ---- Spinner ---- */
.stSpinner > div {
    border-top-color: #3574f0 !important;
}

/* ---- Alert ---- */
.stAlert {
    border-radius: 4px !important;
    border: 1px solid #393b40 !important;
    background: #2b2d30 !important;
}

/* ---- Expander ---- */
.stExpander > details {
    border-radius: 4px !important;
    border: 1px solid #393b40 !important;
    background: #2b2d30 !important;
}

/* ---- Title area ---- */
.app-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #ced0d6;
    margin-bottom: 2px;
}
.app-subtitle {
    font-size: 0.82rem;
    color: #7a7e87;
    margin-bottom: 20px;
}

/* ---- Source link ---- */
.source-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0 4px;
    font-size: 0.85rem;
    color: #7a7e87;
}
.source-bar a {
    color: #6B8EFF;
    text-decoration: none;
}
.source-bar a:hover {
    text-decoration: underline;
    color: #8fa7ff;
}

/* ---- Empty state ---- */
.empty {
    text-align: center;
    padding: 64px 20px;
    color: #5a5e66;
}
.empty p:first-child {
    font-size: 1rem;
    color: #7a7e87;
    margin-bottom: 4px;
}
.empty p:last-child {
    font-size: 0.82rem;
}

/* ---- Compact table inside panels ---- */
.compact-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
}
.compact-table th, .compact-table td {
    border: 1px solid #393b40;
    padding: 5px 10px;
    text-align: left;
}
.compact-table th {
    background: #2b2d30;
    color: #a8adbd;
}

/* ---- Delete button ---- */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #393b40 !important;
    color: #7a7e87 !important;
    border-radius: 4px !important;
    padding: 2px 10px !important;
    font-size: 0.75rem !important;
}
button[kind="secondary"]:hover {
    border-color: #e0556a !important;
    color: #e0556a !important;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
#  Session State
# ================================================================
INIT = {
    "analyzed": False,
    "url": "",
    "page_title": "",
    "text": "",
    "counter": None,
    "stats": None,
    "html_tables": [],
    "csv_data": "",
    "keywords_tfidf": [],
    "keywords_textrank": [],
    "pos_data": None,
    "ngrams": [],
    "url_b": "",
    "analyzed_b": False,
    "title_b": "",
    "text_b": "",
    "counter_b": None,
    "comparison": None,
}
for k, v in INIT.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
#  Sidebar
# ================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 16px;">
        <div style="font-size:1.1rem;font-weight:600;color:#ced0d6;">Text Analyzer</div>
        <div style="font-size:0.75rem;color:#5a5e66;">Web Content Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div style="font-size:0.72rem;font-weight:600;color:#7a7e87;
    letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Filter</div>""",
                unsafe_allow_html=True)

    min_freq = st.slider("Min Frequency", 1, 20, 2,
                         help="Filter words below this count")

    st.markdown("""<div style="font-size:0.72rem;font-weight:600;color:#7a7e87;
    letter-spacing:0.05em;text-transform:uppercase;margin:18px 0 6px;">Chart</div>""",
                unsafe_allow_html=True)

    chart_type = st.selectbox(
        "Chart Type",
        ["词云", "柱状图", "折线图", "饼图", "漏斗图", "散点图",
         "雷达图", "树图", "箱线图（词频分布）"],
        label_visibility="collapsed",
    )

    st.markdown("""<div style="font-size:0.72rem;font-weight:600;color:#7a7e87;
    letter-spacing:0.05em;text-transform:uppercase;margin:18px 0 6px;">Export</div>""",
                unsafe_allow_html=True)

    if st.session_state.analyzed and st.session_state.csv_data:
        safe_name = st.session_state.page_title[:30].replace("/", "_").replace("\\", "_")
        st.download_button(
            label="Export CSV",
            data=st.session_state.csv_data,
            file_name=f"analysis_{safe_name}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("Export HTML Report", use_container_width=True):
            with st.spinner("Generating report..."):
                report = export_html_report(
                    st.session_state.page_title,
                    st.session_state.url,
                    st.session_state.stats,
                    create_chart(chart_type,
                                 Counter({k: v for k, v in st.session_state.counter.items()
                                          if v >= min_freq}).most_common(20)),
                    Counter({k: v for k, v in st.session_state.counter.items()
                            if v >= min_freq}).most_common(20),
                    st.session_state.keywords_tfidf,
                    st.session_state.pos_data,
                    st.session_state.ngrams,
                )
                st.download_button(
                    label="Download HTML Report",
                    data=report,
                    file_name=f"report_{safe_name}.html",
                    mime="text/html",
                    use_container_width=True,
                )

    st.markdown("""<div style="margin-top:24px;padding:12px 0;
    border-top:1px solid #393b40;font-size:0.7rem;color:#5a5e66;line-height:1.6;">
    <p>1. Enter a URL<br>2. Click Analyze<br>3. Browse tabs for insights</p>
    </div>""", unsafe_allow_html=True)

# ================================================================
#  Main Content
# ================================================================
st.markdown('<div class="app-title">Web Text Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Fetch, tokenize, analyze — all from a URL</div>',
    unsafe_allow_html=True,
)

# URL input row
col_url, col_btn = st.columns([5, 1], gap="small")
with col_url:
    url = st.text_input(
        "URL", placeholder="https://example.com/article",
        label_visibility="collapsed", key="url_input",
    )
with col_btn:
    analyze_clicked = st.button("Analyze", use_container_width=True)

# ================================================================
#  Analysis Logic
# ================================================================
if analyze_clicked and url:
    with st.spinner("Fetching page..."):
        try:
            title, text, soup = fetch_page(url)
        except ConnectionError as e:
            st.error(str(e))
            st.stop()
        except ValueError as e:
            st.warning(str(e))
            st.stop()

    with st.spinner("Tokenizing..."):
        counter = cut_words(text)
        stats = get_text_stats(text, counter)
        html_tables = extract_html_tables(soup)

    with st.spinner("Extracting keywords..."):
        kw_tfidf = extract_keywords_tfidf(text, topK=20)
        kw_tr = extract_keywords_textrank(text, topK=20)
        pos_data = get_pos_distribution(text)
        ngrams = get_ngrams(text, n=2, topK=20)

    # Save to history
    try:
        save_analysis(url, title, counter, kw_tfidf, topK=10)
    except Exception:
        pass

    st.session_state.update({
        "analyzed": True, "url": url, "page_title": title, "text": text,
        "counter": counter, "stats": stats, "html_tables": html_tables,
        "keywords_tfidf": kw_tfidf, "keywords_textrank": kw_tr,
        "pos_data": pos_data, "ngrams": ngrams,
        "analyzed_b": False, "comparison": None,
    })
    st.rerun()

# ================================================================
#  Results Display
# ================================================================
if st.session_state.analyzed and st.session_state.counter:
    counter = st.session_state.counter
    filtered = Counter({k: v for k, v in counter.items() if v >= min_freq})
    top20 = filtered.most_common(20)
    chart = create_chart(chart_type, top20)
    st.session_state.csv_data = counter_to_csv(filtered)

    # Source bar
    st.markdown(
        f'<div class="source-bar">'
        f'Source: <a href="{st.session_state.url}" target="_blank">'
        f'{st.session_state.page_title}</a></div>',
        unsafe_allow_html=True,
    )

    # ---- Tabs ----
    t1, t2, t3, t4, t5 = st.tabs([
        "Overview", "Deep Analysis", "Charts", "Compare", "History",
    ])

    # ================================================================
    #  TAB 1: OVERVIEW
    # ================================================================
    with t1:
        stats = st.session_state.stats

        # Metrics row
        cols = st.columns(5)
        for i, (label, val) in enumerate([
            ("Total chars", stats["总字符数（含空格换行）"]),
            ("Words", stats["有效词语数"]),
            ("Unique", stats["唯一词语数"]),
            ("Sentences", stats["句子数"]),
            ("Paragraphs", stats["段落数"]),
        ]):
            accent = " accent" if i == 1 else ""
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card{accent}">
                    <div class="mc-label">{label}</div>
                    <div class="mc-value">{val:,}</div>
                </div>
                """, unsafe_allow_html=True)

        # Secondary metrics
        cols2 = st.columns(3)
        for i, (label, val) in enumerate([
            ("Chars (no space)", stats["有效字符数（去空格换行）"]),
            ("Avg word length", stats["平均词长"]),
            ("Unique ratio", f"{stats['唯一词语数'] / max(1, stats['有效词语数']) * 100:.1f}%"),
        ]):
            with cols2[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="mc-label">{label}</div>
                    <div class="mc-value">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        # Keywords + Chart side by side
        st.markdown("")
        col_kw, col_ch = st.columns([1, 2])
        with col_kw:
            st.markdown("#### Top Keywords (TF-IDF)")
            if st.session_state.keywords_tfidf:
                kw_df = pd.DataFrame(st.session_state.keywords_tfidf, columns=["Word", "Weight"])
                kw_df["Weight"] = kw_df["Weight"].round(4)
                st.dataframe(kw_df, use_container_width=True, hide_index=True, height=370)
            else:
                st.caption("No keywords extracted.")

        with col_ch:
            st.markdown(f"#### Chart — {chart_type}")
            if top20:
                st_pyecharts(chart, height="380px")
            else:
                st.info("No words pass the frequency filter. Lower the threshold in sidebar.")

    # ================================================================
    #  TAB 2: DEEP ANALYSIS
    # ================================================================
    with t2:
        # Row 1: TF-IDF + TextRank keywords
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### TF-IDF Keywords")
            if st.session_state.keywords_tfidf:
                kw_df = pd.DataFrame(st.session_state.keywords_tfidf, columns=["Word", "Weight"])
                kw_df["Weight"] = kw_df["Weight"].round(4)
                kw_df.index = range(1, len(kw_df) + 1)
                st.dataframe(kw_df, use_container_width=True, height=340)
            else:
                st.caption("—")

        with col_b:
            st.markdown("#### TextRank Keywords")
            if st.session_state.keywords_textrank:
                tr_df = pd.DataFrame(st.session_state.keywords_textrank, columns=["Word", "Weight"])
                tr_df["Weight"] = tr_df["Weight"].round(4)
                tr_df.index = range(1, len(tr_df) + 1)
                st.dataframe(tr_df, use_container_width=True, height=340)
            else:
                st.caption("—")

        st.markdown("---")

        # Row 2: POS distribution + N-Grams
        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("#### POS Distribution")
            pos = st.session_state.pos_data
            if pos and pos.get("categories"):
                pos_df = pd.DataFrame(
                    pos["categories"].items(), columns=["Category", "Count"]
                ).sort_values("Count", ascending=False)
                pos_df.index = range(1, len(pos_df) + 1)
                st.dataframe(pos_df, use_container_width=True, height=260)

                # Show named entities if any
                if pos.get("top_entities"):
                    st.markdown("")
                    for ent_type, ent_list in pos["top_entities"].items():
                        if ent_list:
                            st.markdown(f"**{ent_type}** — "
                                        + ", ".join(w for w, _ in ent_list[:8]))
            else:
                st.caption("POS data not available.")

        with col_d:
            st.markdown("#### Top 2-gram Phrases")
            if st.session_state.ngrams:
                ng_df = pd.DataFrame(st.session_state.ngrams, columns=["Phrase", "Count"])
                ng_df.index = range(1, len(ng_df) + 1)
                st.dataframe(ng_df, use_container_width=True, height=260)
            else:
                st.caption("No n-grams extracted.")

        # Row 3: Word co-occurrence network
        st.markdown("---")
        st.markdown("#### Word Co-occurrence Network")
        try:
            graph = create_cooccurrence_graph(filtered)
            st_pyecharts(graph, height="500px")
        except Exception:
            st.caption("Unable to generate co-occurrence graph (insufficient data).")

    # ================================================================
    #  TAB 3: CHARTS
    # ================================================================
    with t3:
        st.markdown(
            f"**Chart:** {chart_type} &nbsp;|&nbsp; "
            f"**Points:** {len(top20)} &nbsp;|&nbsp; "
            f"**Min freq:** {min_freq}"
        )
        if top20:
            st_pyecharts(chart, height="620px")
        else:
            st.info("No words pass the current frequency filter.")
        st.caption("Switch chart type in the sidebar to explore different views.")

        st.markdown("---")
        st.markdown("#### Word Frequency Table")
        if filtered:
            freq_df = pd.DataFrame(filtered.most_common(100), columns=["Word", "Frequency"])
            freq_df.index = range(1, len(freq_df) + 1)
            freq_df.index.name = "Rank"
            st.dataframe(
                freq_df, use_container_width=True, height=400,
                column_config={
                    "Word": st.column_config.TextColumn("Word", width="medium"),
                    "Frequency": st.column_config.NumberColumn("Freq", format="%d"),
                },
            )
            st.caption(
                f"{len(filtered)} words (filtered from {len(counter)}, "
                f"threshold >= {min_freq})"
            )

        # HTML tables
        if st.session_state.html_tables:
            st.markdown("---")
            st.markdown("#### HTML Tables from Page")
            for i, tbl in enumerate(st.session_state.html_tables):
                st.markdown(f"**{tbl['caption']}**")
                if tbl["rows"] and tbl["headers"]:
                    tbl_df = pd.DataFrame(tbl["rows"], columns=tbl["headers"])
                    st.dataframe(tbl_df, use_container_width=True, height=240)
                elif tbl["rows"]:
                    st.dataframe(pd.DataFrame(tbl["rows"]), use_container_width=True, height=240)

    # ================================================================
    #  TAB 4: COMPARE
    # ================================================================
    with t4:
        st.markdown("#### Compare Two URLs")
        st.caption("Analyze a second URL to compare word usage with the current one.")

        col_u, col_go = st.columns([5, 1], gap="small")
        with col_u:
            url_b = st.text_input(
                "Second URL", placeholder="https://example.com/another-article",
                label_visibility="collapsed", key="url_b_input",
            )
        with col_go:
            compare_clicked = st.button("Compare", use_container_width=True)

        if compare_clicked and url_b:
            with st.spinner("Fetching second URL..."):
                try:
                    title_b, text_b, soup_b = fetch_page(url_b)
                except ConnectionError as e:
                    st.error(str(e))
                    st.stop()
                except ValueError as e:
                    st.warning(str(e))
                    st.stop()

            with st.spinner("Analyzing..."):
                counter_b = cut_words(text_b)
                comparison = compare_counters(counter, counter_b)

                st.session_state.url_b = url_b
                st.session_state.title_b = title_b
                st.session_state.text_b = text_b
                st.session_state.counter_b = counter_b
                st.session_state.comparison = comparison
                st.session_state.analyzed_b = True
                st.rerun()

        if st.session_state.analyzed_b and st.session_state.comparison:
            comp = st.session_state.comparison

            # Summary cards
            st.markdown("##### Summary")
            cols = st.columns(4)
            for i, (label, val) in enumerate([
                ("Shared words", comp["shared_count"]),
                ("Only in A", comp["only_a_count"]),
                ("Only in B", comp["only_b_count"]),
                ("Total words B", comp["total_b"]),
            ]):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="mc-label">{label}</div>
                        <div class="mc-value">{val:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Shared words
            col_s, col_o = st.columns(2)
            with col_s:
                st.markdown("##### Top Shared Words")
                if comp["top_shared"]:
                    s_df = pd.DataFrame(comp["top_shared"], columns=["Word", "Total Freq"])
                    st.dataframe(s_df, use_container_width=True, hide_index=True, height=300)
            with col_o:
                st.markdown("##### Unique to Current (A)")
                if comp["top_only_a"]:
                    a_df = pd.DataFrame(comp["top_only_a"], columns=["Word", "Freq"])
                    st.dataframe(a_df, use_container_width=True, hide_index=True, height=300)
                else:
                    st.caption("No unique words.")

            # Comparison chart
            st.markdown("---")
            st.markdown("##### Side-by-side Frequency")
            comp_chart = create_comparison_chart(
                [(w, dict(comp["top_shared"]).get(w, 0)) for w, _ in comp["top_shared"][:10]],
                [(w, dict(comp["top_only_b"]).get(w, 0)) for w, _ in comp["top_only_b"][:10]],
            )
            st_pyecharts(comp_chart, height="450px")

            # Raw text comparison
            with st.expander("View both extracted texts"):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"**A:** {st.session_state.page_title}")
                    st.text_area("A", value=st.session_state.text[:2000], height=300,
                                 disabled=True, label_visibility="collapsed")
                with col_t2:
                    st.markdown(f"**B:** {st.session_state.title_b}")
                    st.text_area("B", value=st.session_state.text_b[:2000], height=300,
                                 disabled=True, label_visibility="collapsed")

    # ================================================================
    #  TAB 5: HISTORY
    # ================================================================
    with t5:
        st.markdown("#### Analysis History")
        try:
            history = get_history(limit=30)
        except Exception:
            history = []

        if history:
            for rec in history:
                with st.expander(
                    f"{rec['title'][:60]} — {rec['created_at']}",
                ):
                    st.markdown(
                        f"**URL:** <{rec['url']}>  |  "
                        f"**Words:** {rec['total_words']}  |  "
                        f"**Unique:** {rec['unique_words']}"
                    )
                    try:
                        top = json.loads(rec.get("top_words", "[]"))
                        if top:
                            st.markdown("**Top words:** " + ", ".join(
                                f"{w}({c})" for w, c in top[:8]
                            ))
                    except (json.JSONDecodeError, TypeError):
                        pass

                    if st.button(f"Delete this record", key=f"del_{rec['id']}"):
                        try:
                            delete_history(rec["id"])
                            st.rerun()
                        except Exception:
                            st.error("Failed to delete.")
            st.caption(f"{len(history)} records")
        else:
            st.markdown("""
            <div class="empty">
                <p>No analysis history yet</p>
                <p>Analyze a URL to automatically save it here.</p>
            </div>
            """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div class="empty">
        <p>Enter a URL above and click "Analyze" to get started.</p>
        <p>Supports Chinese web pages — tokenization, keyword extraction, visualization, and comparison.</p>
    </div>
    """, unsafe_allow_html=True)
