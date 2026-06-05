"""分析历史记录（SQLite）"""
from __future__ import annotations

import json
import logging
import sqlite3
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / ".analysis_history.db"


def _connect() -> sqlite3.Connection:
    """获取数据库连接。"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化表结构（幂等）。"""
    try:
        conn = _connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT DEFAULT '',
                total_words INTEGER DEFAULT 0,
                unique_words INTEGER DEFAULT 0,
                top_words TEXT DEFAULT '[]',
                keywords TEXT DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_created
            ON history(created_at DESC)
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error("初始化历史数据库失败: %s", e)


def save(url: str, title: str, counter: Counter, keywords: list, topK: int = 10) -> bool:
    """保存一次分析记录。返回是否成功。"""
    init_db()
    try:
        conn = _connect()
        top_words = json.dumps(counter.most_common(topK), ensure_ascii=False)
        kw_json = json.dumps(keywords[:topK], ensure_ascii=False)
        conn.execute(
            "INSERT INTO history (url, title, total_words, unique_words, top_words, keywords) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url, title, sum(counter.values()), len(counter), top_words, kw_json),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error("保存历史失败: %s", e)
        return False


def load(limit: int = 50) -> list[dict]:
    """读取最近的分析历史。"""
    init_db()
    try:
        conn = _connect()
        rows = conn.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("读取历史失败: %s", e)
        return []


def remove(history_id: int) -> bool:
    """删除一条记录。"""
    try:
        conn = _connect()
        conn.execute("DELETE FROM history WHERE id = ?", (history_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error("删除历史失败: %s", e)
        return False
