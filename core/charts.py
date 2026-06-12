"""图表工厂 —— pyecharts 封装"""
from __future__ import annotations

from collections import Counter
from typing import Any

from pyecharts import options as opts
from pyecharts.charts import (
    Bar, Boxplot, Funnel, Graph, Line,
    Pie, Radar, Scatter, TreeMap, WordCloud,
)

_C_BLUE = "#6B8EFF"
_C_RED = "#FF6B8E"
_C_BG = "#1e1f22"
_C_TEXT = "#e8eaed"       # 标题 / 主要文字（提亮）
_C_SUB = "#bcc0c7"        # 轴标签 / 次要文字（提亮）
_C_LEGEND = "#c4c7cc"     # 图例 / 饼图标签


def _title_opt(title: str) -> opts.TitleOpts:
    return opts.TitleOpts(
        title=title,
        title_textstyle_opts=opts.TextStyleOpts(color=_C_TEXT, font_size=14),
        pos_left="center",
        pos_top="2%",
    )


def _tooltip_opt(chart_type: str) -> opts.TooltipOpts:
    trigger = "item" if any(t in chart_type for t in ("饼图", "漏斗", "词云", "树图")) else "axis"
    return opts.TooltipOpts(trigger=trigger)


def _xaxis_opt() -> opts.AxisOpts:
    return opts.AxisOpts(
        axislabel_opts=opts.LabelOpts(rotate=45, interval=0, color=_C_SUB),
        name_textstyle_opts=opts.TextStyleOpts(color=_C_SUB),
    )


def _yaxis_opt() -> opts.AxisOpts:
    return opts.AxisOpts(
        axislabel_opts=opts.LabelOpts(color=_C_SUB),
        name_textstyle_opts=opts.TextStyleOpts(color=_C_SUB),
        splitline_opts=opts.SplitLineOpts(
            is_show=True,
            linestyle_opts=opts.LineStyleOpts(color="#2a2c31"),
        ),
    )


def _legend_opt() -> opts.LegendOpts:
    return opts.LegendOpts(
        textstyle_opts=opts.TextStyleOpts(color=_C_LEGEND),
    )


def _label_opt() -> opts.LabelOpts:
    """饼图 / 漏斗图内的标签样式。"""
    return opts.LabelOpts(
        color=_C_LEGEND,
        font_size=11,
    )


def create_chart(chart_type: str, top20: list[tuple[str, int]]) -> Any:
    """根据图表类型和 Top20 数据创建 pyecharts 图表对象。"""
    if not top20:
        return (
            Bar(init_opts=opts.InitOpts(bg_color=_C_BG))
            .add_xaxis([])
            .add_yaxis("", [])
            .set_global_opts(title_opts=opts.TitleOpts(title="暂无数据"))
        )

    words = [w for w, _ in top20]
    freqs = [f for _, f in top20]

    dispatch = {
        "词云": _wordcloud,
        "柱状图": _bar,
        "折线图": _line,
        "饼图": _pie,
        "漏斗图": _funnel,
        "散点图": _scatter,
        "雷达图": _radar,
        "树图": _treemap,
        "箱线图（词频分布）": _boxplot,
    }

    creator = dispatch.get(chart_type, _bar)
    return creator(words, freqs, top20)


def _wordcloud(words, freqs, top20):
    return (
        WordCloud(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add("", top20, word_size_range=[18, 80])
        .set_global_opts(
            title_opts=_title_opt("词云"),
            tooltip_opts=_tooltip_opt("词云"),
        )
    )


def _bar(words, freqs, top20):
    return (
        Bar(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_xaxis(words)
        .add_yaxis("词频", freqs, category_gap="30%", color=_C_BLUE)
        .set_global_opts(
            title_opts=_title_opt("词频柱状图"),
            tooltip_opts=_tooltip_opt("柱状图"),
            xaxis_opts=_xaxis_opt(),
            yaxis_opts=_yaxis_opt(),
            legend_opts=_legend_opt(),
        )
    )


def _line(words, freqs, top20):
    return (
        Line(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_xaxis(words)
        .add_yaxis("词频", freqs, is_smooth=True, color=_C_BLUE)
        .set_global_opts(
            title_opts=_title_opt("词频折线图"),
            tooltip_opts=_tooltip_opt("折线图"),
            xaxis_opts=_xaxis_opt(),
            yaxis_opts=_yaxis_opt(),
            legend_opts=_legend_opt(),
        )
    )


def _pie(words, freqs, top20):
    return (
        Pie(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add("", top20, radius=["40%", "75%"], label_opts=_label_opt())
        .set_global_opts(
            title_opts=_title_opt("词频饼图"),
            tooltip_opts=_tooltip_opt("饼图"),
            legend_opts=_legend_opt(),
        )
    )


def _funnel(words, freqs, top20):
    return (
        Funnel(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add("", top20, sort_="descending", label_opts=_label_opt())
        .set_global_opts(
            title_opts=_title_opt("词频漏斗图"),
            tooltip_opts=_tooltip_opt("漏斗图"),
            legend_opts=_legend_opt(),
        )
    )


def _scatter(words, freqs, top20):
    return (
        Scatter(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_xaxis(words)
        .add_yaxis("词频", freqs, symbol_size=20, color=_C_BLUE)
        .set_global_opts(
            title_opts=_title_opt("词频散点图"),
            tooltip_opts=_tooltip_opt("散点图"),
            xaxis_opts=_xaxis_opt(),
            yaxis_opts=_yaxis_opt(),
            legend_opts=_legend_opt(),
        )
    )


def _radar(words, freqs, top20):
    schema = [
        opts.RadarIndicatorItem(name=w, max_=max(freqs))
        for w in words
    ]
    return (
        Radar(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_schema(
            schema,
            axislabel_opt=opts.LabelOpts(color=_C_SUB),
            splitline_opt=opts.SplitLineOpts(
                linestyle_opts=opts.LineStyleOpts(color="#2a2c31"),
            ),
        )
        .add("词频", [freqs])
        .set_global_opts(
            title_opts=_title_opt("词频雷达图"),
            legend_opts=_legend_opt(),
        )
    )


def _treemap(words, freqs, top20):
    return (
        TreeMap(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add(
            "",
            [{"name": w, "value": f} for w, f in top20],
            label_opts=opts.LabelOpts(color=_C_LEGEND, font_size=12),
            levels=[
                opts.TreeMapLevelsOpts(
                    treemap_itemstyle_opts=opts.TreeMapItemStyleOpts(
                        border_color=_C_BG, border_width=2, gap_width=2,
                    )
                )
            ],
        )
        .set_global_opts(
            title_opts=_title_opt("词频树图"),
            tooltip_opts=_tooltip_opt("树图"),
        )
    )


def _boxplot(words, freqs, top20):
    return (
        Boxplot(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_xaxis(["词频"])
        .add_yaxis("", [freqs])
        .set_global_opts(
            title_opts=_title_opt("词频分布箱线图"),
            yaxis_opts=_yaxis_opt(),
        )
    )


# ---- 词共现网络图 ----

def create_cooccurrence_graph(counter: Counter[str]) -> Graph:
    """基于高频词创建共现网络图。"""
    top_words = [w for w, _ in counter.most_common(40)]
    if len(top_words) < 3:
        return (
            Graph(init_opts=opts.InitOpts(bg_color=_C_BG))
            .add("", [], [])
            .set_global_opts(title_opts=opts.TitleOpts(title="数据不足，无法生成网络图"))
        )

    max_freq = max(1, counter.get(top_words[0], 1))

    nodes = [
        {"name": w, "symbolSize": min(counter[w] / max_freq * 40, 80)}
        for w in top_words[:30]
    ]

    links = [
        {"source": top_words[i], "target": top_words[i + 1]}
        for i in range(len(top_words[:30]) - 1)
    ]

    return (
        Graph(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add(
            "",
            nodes,
            links,
            repulsion=200,
            edge_length=150,
            is_draggable=True,
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(color="#3a3d42", width=1),
            label_opts=opts.LabelOpts(color=_C_LEGEND, font_size=11),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="高频词关系网络",
                title_textstyle_opts=opts.TextStyleOpts(color=_C_TEXT),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item"),
        )
    )


# ---- 对比柱状图 ----

def create_comparison_chart(
    data_a: list[tuple[str, int]],
    data_b: list[tuple[str, int]],
    title: str = "词频对比",
) -> Bar:
    """为对比分析创建并排柱状图。"""
    dict_a = dict(data_a)
    dict_b = dict(data_b)

    all_words = sorted(
        set(dict_a.keys()) | set(dict_b.keys()),
        key=lambda w: dict_a.get(w, 0) + dict_b.get(w, 0),
        reverse=True,
    )[:20]

    return (
        Bar(init_opts=opts.InitOpts(bg_color=_C_BG))
        .add_xaxis(all_words)
        .add_yaxis("A", [dict_a.get(w, 0) for w in all_words], color=_C_BLUE)
        .add_yaxis("B", [dict_b.get(w, 0) for w in all_words], color=_C_RED)
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, title_textstyle_opts=opts.TextStyleOpts(color=_C_TEXT),
            ),
            xaxis_opts=_xaxis_opt(),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(
                textstyle_opts=opts.TextStyleOpts(color=_C_TEXT),
            ),
        )
    )
