"""数据导出（CSV + HTML 报告）"""
from __future__ import annotations

import csv
import io
import time
from collections import Counter


def counter_to_csv(counter: Counter) -> str:
    """将 Counter 转为 UTF-8 BOM CSV（兼容 Excel/WPS）。"""
    output = io.StringIO()
    output.write("﻿")  # BOM
    writer = csv.writer(output)
    writer.writerow(["词语", "词频"])
    for word, freq in counter.most_common():
        writer.writerow([word, freq])
    return output.getvalue()


def html_report(
    title: str,
    url: str,
    stats: dict,
    chart,
    top20: list[tuple[str, int]],
    keywords: list[tuple[str, float]],
    ngrams: list[tuple[str, int]],
) -> str:
    """生成完整 HTML 分析报告。"""
    chart_html = ""
    try:
        chart_html = chart.render_embed()
    except Exception:
        chart_html = "<p>图表渲染失败</p>"

    # 词频表格行
    freq_rows = "".join(
        f"<tr><td>{i}</td><td>{w}</td><td>{f}</td></tr>"
        for i, (w, f) in enumerate(top20, 1)
    )

    # 关键词表格行
    kw_rows = "".join(
        f"<tr><td>{i}</td><td>{w}</td><td>{s:.4f}</td></tr>"
        for i, (w, s) in enumerate(keywords[:20], 1)
    )

    # N-gram 行
    ng_rows = "".join(
        f"<tr><td>{i}</td><td>{ng}</td><td>{c}</td></tr>"
        for i, (ng, c) in enumerate(ngrams[:20], 1)
    )

    # 统计指标卡片
    metric_cards = "".join(
        f'<div class="m"><div class="ml">{k}</div><div class="mv">{v:,}</div></div>'
        for k, v in stats.items()
    )

    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文本分析报告 — {_escape(title)}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
         max-width: 960px; margin: 0 auto; padding: 40px 20px; background: #1e1f22; color: #ced0d6; }}
  h1 {{ color: #6B8EFF; border-bottom: 1px solid #393b40; padding-bottom: 12px; margin-bottom: 8px; }}
  h2 {{ color: #a8adbd; margin: 32px 0 12px; font-size: 1.1rem; }}
  .src {{ color: #7a7e87; font-size: 0.88em; margin-bottom: 24px; }}
  .src a {{ color: #6B8EFF; text-decoration: none; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap: 10px; margin: 16px 0; }}
  .m {{ background: #2b2d30; border: 1px solid #393b40; border-radius: 4px; padding: 14px; text-align: center; }}
  .ml {{ color: #7a7e87; font-size: 0.75rem; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }}
  .mv {{ color: #ced0d6; font-size: 1.4rem; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0 24px; font-size: 0.88em; }}
  th, td {{ border: 1px solid #393b40; padding: 7px 10px; text-align: left; }}
  th {{ background: #2b2d30; color: #a8adbd; font-weight: 600; }}
  tr:nth-child(even) td {{ background: #242529; }}
  .chart {{ margin: 20px 0; }}
  footer {{ margin-top: 40px; padding-top: 14px; border-top: 1px solid #393b40;
            color: #5a5e66; font-size: 0.78em; text-align: center; }}
</style>
</head>
<body>
<h1>文本分析报告</h1>
<p class="src">来源：<a href="{_escape(url)}">{_escape(url)}</a><br>生成时间：{ts}</p>

<h2>统计概览</h2>
<div class="grid">{metric_cards}</div>

<h2>关键词（TF-IDF Top 20）</h2>
<table><thead><tr><th>#</th><th>词语</th><th>权重</th></tr></thead><tbody>{kw_rows}</tbody></table>

<h2>高频短语（2-gram Top 20）</h2>
<table><thead><tr><th>#</th><th>短语</th><th>频次</th></tr></thead><tbody>{ng_rows}</tbody></table>

<h2>词频 Top 20</h2>
<table><thead><tr><th>#</th><th>词语</th><th>词频</th></tr></thead><tbody>{freq_rows}</tbody></table>

<h2>可视化图表</h2>
<div class="chart">{chart_html}</div>

<footer>Web Text Analyzer &middot; {ts}</footer>
</body>
</html>"""


def _escape(s: str) -> str:
    """HTML 实体转义。"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
