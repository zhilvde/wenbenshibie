"""核心模块 —— 网页抓取、文本分析、图表生成"""
from core.fetcher import fetch_page
from core.analyzer import (
    cut_words, get_text_stats,
    extract_keywords_tfidf, extract_keywords_textrank,
    get_pos_distribution, get_ngrams, compare_counters,
    extract_html_tables,
)
from core.charts import (
    create_chart, create_comparison_chart, create_cooccurrence_graph,
)
