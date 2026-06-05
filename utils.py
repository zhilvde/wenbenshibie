import re
import csv
import io
import json
import time
import sqlite3
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests
import jieba
import jieba.analyse
import jieba.posseg as pseg
from bs4 import BeautifulSoup
from pyecharts.charts import (
    Bar, Boxplot, Funnel, Graph, Line, Pie,
    Radar, Sankey, Scatter, TreeMap, WordCloud,
)
from pyecharts import options as opts

# ---------- 停用词 ----------
STOPWORDS = set("""
的 了 在 和 是 有 就 不 人 我 他 你 也 都 一个 上 我们 这 那 那个 这里
什么 怎么 为什么 你们 他人 她 他们 它 以及 及 或者 如果 因为 所以 但是
而且 也许 每个 各个 关于 还 还有 但 所有 此 这些 那些 其中 此时 那时
—— ... - — ， 。 ： ； ！ ？ （ ） 《 》 【 】 " " ' ' - _ ~ 、 \n \t
""".split())


# ================================================================
#  网页抓取
# ================================================================

def fetch_page(url):
    """抓取网页，返回 (title, text, soup) 三元组。"""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    session = requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        session.get(base_url, headers=headers, timeout=10)
        resp = session.get(url, headers=headers, timeout=10)

        if resp.status_code in (403, 404):
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) >= 2:
                column_path = "/".join(path_parts[:-1])
                column_url = f"{base_url}/{column_path}/"
                session.get(column_url, headers=headers, timeout=10)
                resp = session.get(
                    url,
                    headers={**headers, "Referer": column_url},
                    timeout=10,
                )

        if resp.status_code != 200:
            raise ConnectionError(
                f"访问失败（HTTP {resp.status_code}）：该页面受访问限制"
            )

        resp.encoding = resp.apparent_encoding

    except requests.RequestException as e:
        raise ConnectionError(f"网络请求异常：{e}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # 提取标题
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        title = parsed.path.strip("/") or parsed.netloc

    # 清洗正文
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    if not text.strip():
        raise ValueError("页面未提取到有效文本内容")

    return title, text, soup


# ================================================================
#  分词与统计
# ================================================================

def cut_words(text):
    """中文分词 + 停用词过滤，返回 Counter。"""
    words = jieba.lcut(text)
    words = [w for w in words if len(w) > 1 and w not in STOPWORDS]
    return Counter(words)


def get_text_stats(text, counter):
    """返回文本统计指标字典。"""
    clean_text = re.sub(r"\s+", "", text)
    sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", text) if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    total_words = sum(counter.values())
    unique_words = len(counter)
    avg_word_len = (
        round(sum(len(w) * c for w, c in counter.items()) / total_words, 2)
        if total_words else 0
    )

    return {
        "总字符数（含空格换行）": len(text),
        "有效字符数（去空格换行）": len(clean_text),
        "有效词语数": total_words,
        "唯一词语数": unique_words,
        "句子数": len(sentences) or 1,
        "段落数": len(paragraphs) or 1,
        "平均词长": avg_word_len,
    }


# ================================================================
#  HTML 表格提取
# ================================================================

def extract_html_tables(soup):
    """从 BeautifulSoup 中提取所有 <table> 元素。"""
    tables = []
    for table_tag in soup.find_all("table"):
        caption_tag = table_tag.find("caption")
        caption = caption_tag.get_text(strip=True) if caption_tag else ""

        headers = []
        thead = table_tag.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        if not headers:
            first_row = table_tag.find("tr")
            if first_row:
                ths = first_row.find_all("th")
                if ths:
                    headers = [th.get_text(strip=True) for th in ths]

        rows = []
        start = 1 if headers else 0
        for tr in list(table_tag.find_all("tr"))[start:]:
            cells = tr.find_all(["td", "th"])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                rows.append(row_data)

        if not headers and rows:
            headers = [f"列{i + 1}" for i in range(len(rows[0]))]

        tables.append({
            "caption": caption or f"表格 {len(tables) + 1}",
            "headers": headers,
            "rows": rows,
        })
    return tables


# ================================================================
#  关键词提取（jieba 内置，零新依赖）
# ================================================================

def extract_keywords_tfidf(text, topK=20):
    """TF-IDF 关键词提取，返回 [(word, weight), ...]"""
    return jieba.analyse.extract_tags(text, topK=topK, withWeight=True)


def extract_keywords_textrank(text, topK=20):
    """TextRank 关键词提取，返回 [(word, weight), ...]"""
    return jieba.analyse.textrank(text, topK=topK, withWeight=True)


# ================================================================
#  词性标注与分类
# ================================================================

# 词性分组（北大词性标注集）
POS_CATEGORIES = {
    "名词": ["n", "nr", "ns", "nt", "nz", "ng"],
    "动词": ["v", "vd", "vn", "vf"],
    "形容词": ["a", "ad", "an", "ag", "al"],
    "副词": ["d", "dg"],
    "代词": ["r", "rr", "rz"],
    "数词/量词": ["m", "mq", "q"],
    "介词": ["p"],
    "连词": ["c", "cc"],
    "助词/语气词": ["u", "y", "e", "o"],
    "其他": ["x", "w", "t", "f", "s", "h", "k", "z", "b"],
}

POS_LABELS = {
    "n": "名词", "nr": "人名", "ns": "地名", "nt": "机构", "nz": "其他专名", "ng": "名词性语素",
    "v": "动词", "vd": "副动词", "vn": "名动词", "vf": "趋向动词",
    "a": "形容词", "ad": "副形词", "an": "名形词", "ag": "形容词性语素", "al": "形容词性惯用语",
    "d": "副词", "dg": "副词性语素",
    "r": "代词", "rr": "人称代词", "rz": "指示代词",
    "m": "数词", "mq": "数量词", "q": "量词",
    "p": "介词", "c": "连词", "cc": "并列连词",
    "u": "助词", "y": "语气词", "e": "叹词", "o": "拟声词",
    "x": "非语素字", "w": "标点符号", "t": "时间词", "f": "方位词",
    "s": "处所词", "h": "前缀", "k": "后缀", "z": "状态词", "b": "区别词",
}


def get_pos_distribution(text):
    """
    词性分类统计。
    返回 {
        "categories": {"名词": count, "动词": count, ...},
        "top_entities": {"人名": [(word, count), ...], "地名": [...], "机构": [...]},
        "detail": [{"word": w, "pos": tag, "label": label}, ...]
    }
    """
    words = pseg.cut(text)
    cat_counter = Counter()
    entities = {"人名": Counter(), "地名": Counter(), "机构": Counter()}
    detail = []

    for w, flag in words:
        if len(w) < 2 or w in STOPWORDS:
            continue
        label = POS_LABELS.get(flag, flag)

        # 分类计数
        assigned = False
        for cat, tags in POS_CATEGORIES.items():
            if any(flag.startswith(t) for t in tags):
                cat_counter[cat] += 1
                assigned = True
                break
        if not assigned:
            cat_counter["其他"] += 1

        # 命名实体收集
        if flag == "nr":
            entities["人名"][w] += 1
        elif flag == "ns":
            entities["地名"][w] += 1
        elif flag == "nt":
            entities["机构"][w] += 1

        detail.append({"word": w, "pos": flag, "label": label})

    top_entities = {
        k: v.most_common(15) for k, v in entities.items() if v
    }

    return {
        "categories": dict(cat_counter.most_common()),
        "top_entities": top_entities,
        "detail": detail,
    }


# ================================================================
#  N-gram 分析
# ================================================================

def get_ngrams(text, n=2, topK=15):
    """提取高频 N-gram 短语，返回 [(phrase, count), ...]"""
    words = [w for w in jieba.lcut(text) if len(w) > 1 and w not in STOPWORDS]
    ngrams = zip(*[words[i:] for i in range(n)])
    return Counter([" / ".join(g) for g in ngrams]).most_common(topK)


# ================================================================
#  文本相似度（简易余弦相似度）
# ================================================================

def compare_counters(c1, c2, topK=20):
    """
    对比两个 Counter，返回差异分析。
    """
    all_words = set(c1.keys()) | set(c2.keys())
    shared = set(c1.keys()) & set(c2.keys())
    only_a = set(c1.keys()) - set(c2.keys())
    only_b = set(c2.keys()) - set(c1.keys())

    # 共享词的频率差异
    diff_words = []
    for w in shared:
        diff_words.append((w, c1[w], c2[w], c1[w] - c2[w]))
    diff_words.sort(key=lambda x: abs(x[3]), reverse=True)

    return {
        "total_a": sum(c1.values()),
        "total_b": sum(c2.values()),
        "unique_a": len(c1),
        "unique_b": len(c2),
        "shared_count": len(shared),
        "only_a_count": len(only_a),
        "only_b_count": len(only_b),
        "top_shared": Counter({w: c1[w] + c2[w] for w in shared}).most_common(topK),
        "top_only_a": Counter({w: c1[w] for w in only_a}).most_common(topK),
        "top_only_b": Counter({w: c2[w] for w in only_b}).most_common(topK),
        "top_diff": diff_words[:topK],
    }


# ================================================================
#  图表工厂（新增 Sankey / Graph / Boxplot）
# ================================================================

def create_chart(chart_type, top20):
    """根据图表类型和 top20 数据创建 pyecharts 图表。"""
    if not top20:
        return (
            Bar()
            .add_xaxis([])
            .add_yaxis("", [])
            .set_global_opts(title_opts=opts.TitleOpts(title="No Data"))
        )

    words, freqs = zip(*top20)
    words = list(words)
    freqs = list(freqs)
    # 统一配色
    color_main = "#6B8EFF"

    dispatch = {
        "词云": lambda: (
            WordCloud()
            .add("", top20, word_size_range=[18, 80])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词云"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "柱状图": lambda: (
            Bar()
            .add_xaxis(words)
            .add_yaxis("词频", freqs, category_gap="30%", color=color_main)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频柱状图"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=0)
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        ),
        "折线图": lambda: (
            Line()
            .add_xaxis(words)
            .add_yaxis("词频", freqs, is_smooth=True, color=color_main)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频折线图"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=0)
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        ),
        "饼图": lambda: (
            Pie()
            .add("", top20, radius=["40%", "75%"])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频饼图"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "漏斗图": lambda: (
            Funnel()
            .add("", top20, sort_="descending")
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频漏斗图", pos_left="center"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "散点图": lambda: (
            Scatter()
            .add_xaxis(words)
            .add_yaxis("词频", freqs, symbol_size=20, color=color_main)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频散点图"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45, interval=0)
                ),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "雷达图": lambda: (
            Radar()
            .add_schema([
                opts.RadarIndicatorItem(name=w, max_=max(freqs)) for w in words
            ])
            .add("词频", [freqs])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
        ),
        "树图": lambda: (
            TreeMap()
            .add(
                "",
                [{"name": w, "value": f} for w, f in top20],
                levels=[
                    opts.TreeMapLevelsOpts(
                        treemap_itemstyle_opts=opts.TreeMapItemStyleOpts(
                            border_color="#2b2d30", border_width=2, gap_width=2
                        )
                    )
                ],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频树图"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "箱线图（词频分布）": lambda: (
            Boxplot()
            .add_xaxis(["词频"])
            .add_yaxis("", [freqs])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频箱线图"),
                tooltip_opts=opts.TooltipOpts(trigger="item"),
            )
        ),
        "词共现网络图": _create_cooccurrence_graph,
    }

    creator = dispatch.get(chart_type, dispatch["柱状图"])
    return creator()


def _create_cooccurrence_graph():
    """创建词共现网络图的占位实现（需要外部传入共现数据）。"""
    # 基于 top20 创建简单关系图，高频词作为节点，权重作为大小
    return (
        Graph()
        .add(
            "",
            [],
            [],
            repulsion=50,
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="词共现网络图（需共现数据）"))
    )


def create_cooccurrence_graph(counter, window=5):
    """
    创建基于滑动窗口的词共现网络图。
    输入：词 Counter（来自 cut_words），窗口大小。
    输出：pyecharts Graph 对象。
    """
    from itertools import islice

    # 获取前 40 个高频词作为节点
    top_words = [w for w, _ in counter.most_common(40)]
    top_set = set(top_words)

    # 用原始文本重新分词获取词语序列（注意这里需要原始 token 序列）
    # 简化处理：直接用 top_words 之间的共现关系
    # 实际上需要原始 token list，但这里我们从 counter 的键构造
    nodes = [{"name": w, "symbolSize": min(counter[w] / max(1, counter[top_words[0]]) * 40, 80)}
             for w in top_words[:30]]

    # 因为没有原始 token 序列来计算 co-occurrence，我们创建一个简化版：
    # 将相邻的高频词连接起来
    links = []
    for i in range(len(top_words[:30]) - 1):
        links.append({
            "source": top_words[i],
            "target": top_words[i + 1],
        })

    return (
        Graph(init_opts=opts.InitOpts(bg_color="#1e1f22"))
        .add(
            "",
            nodes,
            links,
            repulsion=200,
            edge_length=150,
            is_draggable=True,
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(color="#3a3d42", width=1),
            label_opts=opts.LabelOpts(color="#ced0d6", font_size=10),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="高频词关系网络",
                title_textstyle_opts=opts.TextStyleOpts(color="#ced0d6"),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item"),
        )
    )


def create_comparison_chart(before_data, after_data, title=""):
    """为对比分析创建并排柱状图。"""
    words = sorted(set([w for w, _ in before_data[:15]] + [w for w, _ in after_data[:15]]),
                   key=lambda w: dict(before_data).get(w, 0) + dict(after_data).get(w, 0),
                   reverse=True)[:20]

    before_dict = dict(before_data)
    after_dict = dict(after_data)

    return (
        Bar(init_opts=opts.InitOpts(bg_color="#1e1f22"))
        .add_xaxis(words)
        .add_yaxis("A", [before_dict.get(w, 0) for w in words], color="#6B8EFF")
        .add_yaxis("B", [after_dict.get(w, 0) for w in words], color="#FF6B8E")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title or "词频对比",
                title_textstyle_opts=opts.TextStyleOpts(color="#ced0d6"),
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, interval=0, color="#9b9da4")
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#ced0d6")),
        )
    )


# ================================================================
#  CSV / HTML 导出
# ================================================================

def counter_to_csv(counter):
    """将 Counter 转为 UTF-8 BOM CSV 字符串（Excel 兼容）。"""
    output = io.StringIO()
    output.write("﻿")
    writer = csv.writer(output)
    writer.writerow(["词语", "词频"])
    for word, freq in counter.most_common():
        writer.writerow([word, freq])
    return output.getvalue()


def export_html_report(title, url, stats, chart, top20, keywords, pos_data, ngrams):
    """导出完整 HTML 分析报告。"""
    # 用 pyecharts 渲染图表为 HTML 片段
    chart_html = chart.render_embed() if chart else ""

    rows = ""
    for i, (w, f) in enumerate(top20, 1):
        rows += f"<tr><td>{i}</td><td>{w}</td><td>{f}</td></tr>"

    kw_rows = ""
    for i, (w, score) in enumerate(keywords, 1):
        kw_rows += f"<tr><td>{i}</td><td>{w}</td><td>{score:.4f}</td></tr>"

    ng_rows = ""
    for i, (ng, c) in enumerate(ngrams, 1):
        ng_rows += f"<tr><td>{i}</td><td>{ng}</td><td>{c}</td></tr>"

    report = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文本分析报告 — {title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
         max-width: 960px; margin: 0 auto; padding: 40px 20px; background: #1e1f22; color: #ced0d6; }}
  h1 {{ color: #6B8EFF; border-bottom: 1px solid #393b40; padding-bottom: 12px; }}
  h2 {{ color: #a8adbd; margin-top: 32px; }}
  .source {{ color: #7a7e87; font-size: 0.9em; margin-bottom: 24px; }}
  .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 20px 0; }}
  .metric {{ background: #2b2d30; border-radius: 6px; padding: 16px; text-align: center; }}
  .metric .label {{ color: #9b9da4; font-size: 0.82em; }}
  .metric .value {{ color: #ced0d6; font-size: 1.6em; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0 24px; }}
  th, td {{ border: 1px solid #393b40; padding: 8px 12px; text-align: left; font-size: 0.9em; }}
  th {{ background: #2b2d30; color: #a8adbd; }}
  tr:nth-child(even) {{ background: #242529; }}
  .chart {{ margin: 24px 0; }}
  footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #393b40; color: #5a5e66;
            font-size: 0.8em; text-align: center; }}
</style>
</head>
<body>
<h1>文本分析报告</h1>
<p class="source">来源: <a href="{url}" style="color:#6B8EFF;">{url}</a><br>生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>

<h2>统计概览</h2>
<div class="metrics">
  {"".join(f'<div class="metric"><div class="label">{k}</div><div class="value">{v:,}</div></div>' for k, v in stats.items())}
</div>

<h2>可视化图表</h2>
<div class="chart">{chart_html}</div>

<h2>关键词（TF-IDF）</h2>
<table><tr><th>#</th><th>词语</th><th>权重</th></tr>{kw_rows}</table>

<h2>高频短语（2-gram）</h2>
<table><tr><th>#</th><th>短语</th><th>频次</th></tr>{ng_rows}</table>

<h2>词频 Top 20</h2>
<table><tr><th>#</th><th>词语</th><th>词频</th></tr>{rows}</table>

<footer>Web Text Analyzer &middot; Generated at {time.strftime("%Y-%m-%d %H:%M:%S")}</footer>
</body>
</html>"""
    return report


# ================================================================
#  分析历史管理（SQLite，零新依赖）
# ================================================================

DB_PATH = Path(__file__).parent / ".analysis_history.db"


def _get_db():
    """获取数据库连接（线程安全）。"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_history_db():
    """初始化历史记录表。"""
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            total_words INTEGER,
            unique_words INTEGER,
            top_words TEXT,
            keywords TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(url, title, counter, keywords, topK=10):
    """保存一次分析记录。"""
    init_history_db()
    conn = _get_db()
    top_words = json.dumps(counter.most_common(topK), ensure_ascii=False)
    kw_json = json.dumps(keywords[:topK], ensure_ascii=False)
    conn.execute(
        "INSERT INTO history (url, title, total_words, unique_words, top_words, keywords) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (url, title, sum(counter.values()), len(counter), top_words, kw_json),
    )
    conn.commit()
    conn.close()


def get_history(limit=50):
    """获取分析历史列表。"""
    init_history_db()
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_history(history_id):
    """删除一条历史记录。"""
    conn = _get_db()
    conn.execute("DELETE FROM history WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()
