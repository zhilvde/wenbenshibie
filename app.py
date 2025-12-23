import streamlit as st
import requests
import jieba
from bs4 import BeautifulSoup
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Funnel, Radar, Scatter
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
from urllib.parse import urlparse

st.set_page_config(page_title="文本分析系统", layout="wide")

# ------------------ 停用词 ------------------
STOPWORDS = set("""
的 了 在 和 是 有 就 不 人 我 他 你 也 都 一个 上 我们 这 那 那个 这里
什么 怎么 为什么 你们 他人 她 他们 它 以及 及 或者 如果 因为 所以 但是
而且 也许 每个 各个 关于 还 还有 但 所有 此 这些 那些 其中 此时 那时
—— … – — ， 。 ： ； ！ ？ （ ） 《 》 【 】 “ ” ‘ ’ - _ ~ 、 \n \t  
""".split())

# ------------------ 工具函数 ------------------
def fetch_text(url):
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
        "Accept-Language": "zh-CN,zh;q=0.9"
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
                    timeout=10
                )

        if resp.status_code != 200:
            st.error(f"访问失败（HTTP {resp.status_code}）：该页面受访问限制")
            st.stop()

        resp.encoding = resp.apparent_encoding

    except requests.RequestException as e:
        st.error(f"网络请求异常：{e}")
        st.stop()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    return text

# ------------------ 分词 + 停用词过滤 ------------------
def cut_words(text):
    words = jieba.lcut(text)
    words = [w for w in words if len(w) > 1 and w not in STOPWORDS]
    return Counter(words)

# ------------------ UI ------------------
st.title("基于 Streamlit 的文本词频分析系统")

url = st.text_input("请输入文章 URL：")

min_freq = st.sidebar.slider("最低词频过滤", 1, 20, 2)

chart_type = st.sidebar.selectbox(
    "选择图形类型",
    ["词云", "柱状图", "折线图", "饼图", "漏斗图", "散点图", "雷达图"]
)

if st.button("开始分析") and url:
    with st.spinner("正在抓取文本并分析..."):
        text = fetch_text(url)
        counter = cut_words(text)

        # 低频过滤
        counter = Counter({k: v for k, v in counter.items() if v >= min_freq})
        top20 = counter.most_common(20)

    st.subheader(" 词频 Top20")
    st.table(top20)

    words, freqs = zip(*top20)

    # ------------------ 图形 ------------------
    if chart_type == "词云":
        c = (
            WordCloud()
            .add("", top20, word_size_range=[20, 80])
            .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
        )

    elif chart_type == "柱状图":
        c = (
            Bar()
            .add_xaxis(list(words))
            .add_yaxis("词频", list(freqs))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频柱状图"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, interval=0))
            )
        )

    elif chart_type == "折线图":
        c = (
            Line()
            .add_xaxis(list(words))
            .add_yaxis("词频", list(freqs))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频折线图"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, interval=0))
            )
        )

    elif chart_type == "饼图":
        c = (
            Pie()
            .add("", top20)
            .set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
        )

    elif chart_type == "漏斗图":
        c = (
            Funnel()
            .add("", top20)
            .set_global_opts(title_opts=opts.TitleOpts(title="词频漏斗图"))
        )

    elif chart_type == "散点图":
        c = (
            Scatter()
            .add_xaxis(list(words))
            .add_yaxis("词频", list(freqs))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词频散点图"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, interval=0))
            )
        )

    elif chart_type == "雷达图":
        schema = [opts.RadarIndicatorItem(name=w, max_=max(freqs)) for w in words]
        c = (
            Radar()
            .add_schema(schema)
            .add("词频", [list(freqs)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
        )
        

    st_pyecharts(c, height="500px")
