"""网页抓取模块"""
from __future__ import annotations

import logging
import re
from typing import Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 请求头
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# URL 验证正则
_URL_RE = re.compile(
    r"^https?://"  # 协议
    r"[^\s/$.?#]+\.[^\s]*$",  # 域名 + 路径
    re.IGNORECASE,
)

# 连接/读取超时（秒）
_CONNECT_TIMEOUT = 8
_READ_TIMEOUT = 15


def _validate_url(url: str) -> str:
    """校验并规范化 URL。"""
    url = url.strip()
    if not url:
        raise ValueError("URL 不能为空")

    # 自动补协议
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # 格式校验
    if not _URL_RE.match(url):
        raise ValueError(f"URL 格式无效：{url}")

    return url


def _build_session() -> requests.Session:
    """构造带重试的 Session。"""
    session = requests.Session()
    session.headers.update(_HEADERS)
    # 连接池
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=1,
        pool_maxsize=2,
        max_retries=1,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_page(url: str) -> Tuple[str, str, BeautifulSoup]:
    """
    抓取网页内容。

    Args:
        url: 目标网页地址。

    Returns:
        (页面标题, 清洗后文本, BeautifulSoup 对象)

    Raises:
        ValueError: URL 无效或页面无有效文本。
        ConnectionError: 网络请求失败或 HTTP 状态码异常。
    """
    url = _validate_url(url)
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    session = _build_session()

    # --- 主请求 ---
    try:
        # 先访问首页建立 cookie（模拟正常浏览）
        try:
            session.get(base_url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
        except requests.RequestException:
            pass  # 首页失败不阻断

        resp = session.get(url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))

        # 403/404 时尝试 Referer 回退
        if resp.status_code in (403, 404):
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            if len(path_parts) >= 2:
                column_url = f"{base_url}/{'/'.join(path_parts[:-1])}/"
                try:
                    session.get(column_url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
                except requests.RequestException:
                    pass
                resp = session.get(
                    url,
                    headers={"Referer": column_url},
                    timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT),
                )

        if resp.status_code != 200:
            raise ConnectionError(
                f"访问失败（HTTP {resp.status_code}），该页面可能受访问限制或不存在"
            )

    except requests.Timeout:
        raise ConnectionError("请求超时，请检查网络连接或稍后重试")
    except requests.ConnectionError:
        raise ConnectionError("网络连接失败，请确认网址可访问")
    except requests.RequestException as e:
        raise ConnectionError(f"网络请求异常：{e}")

    # --- 解析 ---
    # 编码检测
    if resp.encoding and resp.encoding.lower() in ("iso-8859-1", "latin-1"):
        # requests 猜测失败时手动检测
        match = re.search(
            rb'<meta[^>]+charset=["\']?([^"\'>;\s]+)',
            resp.content[:4096],
            re.IGNORECASE,
        )
        if match:
            resp.encoding = match.group(1).decode("ascii", errors="ignore")
        else:
            resp.encoding = resp.apparent_encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")

    # --- 提取标题 ---
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        title = parsed.path.strip("/") or parsed.netloc
    # 清理标题中的换行和多余空格
    title = re.sub(r"\s+", " ", title).strip()

    # --- 清洗正文 ---
    for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    if not text.strip():
        raise ValueError("页面未提取到有效文本内容，可能为纯图片/视频页面或需要登录")

    logger.info("抓取成功: %s (%d 字符)", title, len(text))
    return title, text, soup


def fetch_pages_batch(urls: list[str]) -> list[Tuple[str, str, str, BeautifulSoup]]:
    """
    批量抓取多个 URL（串行，避免被封）。

    Returns:
        [(url, title, text, soup), ...]，失败的返回空字符串。
    """
    results = []
    for url in urls:
        try:
            title, text, soup = fetch_page(url)
            results.append((url, title, text, soup))
        except (ValueError, ConnectionError) as e:
            logger.warning("批量抓取失败 [%s]: %s", url, e)
            results.append((url, "", f"[失败] {e}", None))
    return results
