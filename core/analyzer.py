"""文本分析模块 —— 分词、统计、关键词、词性、N-gram"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Tuple

import jieba
import jieba.analyse
import jieba.posseg as pseg
from bs4 import BeautifulSoup

from data import STOPWORDS

# ---------- 词性分组 ----------

POS_LABELS: dict[str, str] = {
    "n": "名词", "nr": "人名", "ns": "地名", "nt": "机构名", "nz": "其他专名",
    "v": "动词", "vd": "副动词", "vn": "名动词",
    "a": "形容词", "ad": "副形词", "an": "名形词",
    "d": "副词", "r": "代词", "m": "数词", "q": "量词",
    "p": "介词", "c": "连词", "u": "助词", "y": "语气词",
    "t": "时间词", "f": "方位词", "s": "处所词",
    "e": "叹词", "o": "拟声词", "x": "非语素字", "w": "标点",
}

POS_CATEGORIES: dict[str, list[str]] = {
    "名词": ["n", "nr", "ns", "nt", "nz", "ng"],
    "动词": ["v", "vd", "vn", "vf"],
    "形容词": ["a", "ad", "an", "ag", "al"],
    "副词": ["d", "dg"],
    "代词": ["r", "rr", "rz"],
    "数词/量词": ["m", "mq", "q"],
    "介词/连词": ["p", "c", "cc"],
    "助词/语气": ["u", "y", "e", "o"],
    "其他": ["x", "w", "t", "f", "s", "h", "k", "z", "b"],
}

ENTITY_TAGS = {"nr": "人名", "ns": "地名", "nt": "机构名"}


# ---------- 分词 ----------

def cut_words(text: str) -> Counter[str]:
    """中文分词 + 停用词过滤。"""
    if not text or not text.strip():
        return Counter()
    words = jieba.lcut(text)
    return Counter(w for w in words if len(w) > 1 and w not in STOPWORDS)


# ---------- 文本统计 ----------

def get_text_stats(text: str, counter: Counter[str]) -> dict[str, int | float]:
    """计算文本统计指标。"""
    stats: dict[str, int | float] = {}
    stats["总字符数（含空格换行）"] = len(text)

    clean = re.sub(r"\s+", "", text)
    stats["有效字符数（去空格换行）"] = len(clean)

    total_words = sum(counter.values())
    unique_words = len(counter)
    stats["有效词语数"] = total_words
    stats["唯一词语数"] = unique_words

    # 句子数
    sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", text) if s.strip()]
    stats["句子数"] = len(sentences) or 1

    # 段落数
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    stats["段落数"] = len(paragraphs) or 1

    # 平均词长
    if total_words > 0:
        stats["平均词长"] = round(
            sum(len(w) * c for w, c in counter.items()) / total_words, 2
        )
    else:
        stats["平均词长"] = 0.0

    return stats


# ---------- 关键词 ----------

def extract_keywords_tfidf(text: str, topK: int = 20) -> list[tuple[str, float]]:
    """TF-IDF 关键词提取。（jieba 内置，零额外依赖）"""
    if not text or not text.strip():
        return []
    return jieba.analyse.extract_tags(text, topK=topK, withWeight=True)


def extract_keywords_textrank(text: str, topK: int = 20) -> list[tuple[str, float]]:
    """TextRank 关键词提取。（jieba 内置）"""
    if not text or not text.strip():
        return []
    return jieba.analyse.textrank(text, topK=topK, withWeight=True)


# ---------- 词性标注 ----------

def get_pos_distribution(text: str) -> dict:
    """
    词性分类 + 命名实体识别。

    Returns:
        {
            "categories": {"名词": 123, "动词": 45, ...},
            "entities": {"人名": [(word, count), ...], "地名": [...], "机构名": [...]}
        }
    """
    if not text or not text.strip():
        return {"categories": {}, "entities": {}}

    words = pseg.cut(text)
    cat_counter: Counter[str] = Counter()
    entities: dict[str, Counter[str]] = {
        "人名": Counter(), "地名": Counter(), "机构名": Counter(),
    }

    for w, flag in words:
        if len(w) < 2 or w in STOPWORDS:
            continue

        # 词性分类
        assigned = False
        for cat, tags in POS_CATEGORIES.items():
            if any(flag.startswith(t) for t in tags):
                cat_counter[cat] += 1
                assigned = True
                break
        if not assigned:
            cat_counter["其他"] += 1

        # 命名实体
        if flag in ENTITY_TAGS:
            entities[ENTITY_TAGS[flag]][w] += 1

    return {
        "categories": dict(cat_counter.most_common()),
        "entities": {
            label: cnt.most_common(15)
            for label, cnt in entities.items() if cnt
        },
    }


# ---------- N-gram ----------

def get_ngrams(text: str, n: int = 2, topK: int = 20) -> list[tuple[str, int]]:
    """提取高频 N-gram 短语。"""
    if not text or not text.strip():
        return []
    words = [w for w in jieba.lcut(text) if len(w) > 1 and w not in STOPWORDS]
    if len(words) < n:
        return []
    ngrams = zip(*(words[i:] for i in range(n)))
    return Counter(" / ".join(g) for g in ngrams).most_common(topK)


# ---------- 文本对比 ----------

def compare_counters(
    c1: Counter[str], c2: Counter[str], topK: int = 20,
) -> dict:
    """对比两个词频 Counter 的差异。"""
    all_words = set(c1.keys()) | set(c2.keys())
    shared = set(c1.keys()) & set(c2.keys())
    only_1 = set(c1.keys()) - set(c2.keys())
    only_2 = set(c2.keys()) - set(c1.keys())

    # 差异排序
    diffs = [(w, c1[w], c2[w], c1[w] - c2[w]) for w in shared]
    diffs.sort(key=lambda x: abs(x[3]), reverse=True)

    return {
        "total_1": sum(c1.values()),
        "total_2": sum(c2.values()),
        "unique_1": len(c1),
        "unique_2": len(c2),
        "shared": len(shared),
        "only_1_count": len(only_1),
        "only_2_count": len(only_2),
        "top_shared": Counter({w: c1[w] + c2[w] for w in shared}).most_common(topK),
        "top_only_1": Counter({w: c1[w] for w in only_1}).most_common(topK),
        "top_only_2": Counter({w: c2[w] for w in only_2}).most_common(topK),
        "top_diff": diffs[:topK],
    }


# ---------- HTML 表格提取 ----------

def extract_html_tables(soup: BeautifulSoup | None) -> list[dict]:
    """从 BeautifulSoup 提取所有 <table>。"""
    if soup is None:
        return []

    tables: list[dict] = []
    for table_tag in soup.find_all("table"):
        # 标题
        caption_tag = table_tag.find("caption")
        caption = caption_tag.get_text(strip=True) if caption_tag else ""

        # 表头
        headers: list[str] = []
        thead = table_tag.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        if not headers:
            first_row = table_tag.find("tr")
            if first_row:
                ths = first_row.find_all("th")
                if ths:
                    headers = [th.get_text(strip=True) for th in ths]

        # 数据行
        rows: list[list[str]] = []
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
