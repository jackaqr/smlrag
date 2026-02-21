"""
配置存储 - 使用 SQLite 持久化模型配置、界面设置等。
仅存储配置信息，资源占用极小（单文件几 MB 内）。
"""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# 数据库文件放在 backend/data/config.db，若不存在则创建目录
_BASE = Path(__file__).resolve().parent.parent
_DB_PATH = os.getenv("CONFIG_DB_PATH", str(_BASE / "data" / "config.db"))


def _ensure_dir() -> None:
    d = os.path.dirname(_DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    _ensure_dir()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def get(key: str) -> Optional[Any]:
    """按 key 读取配置，返回解析后的 JSON；不存在返回 None。"""
    conn = _get_conn()
    try:
        _init_db(conn)
        row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return json.loads(row["value"])
    finally:
        conn.close()


def set(key: str, value: Any) -> None:
    """写入配置，value 将按 JSON 序列化存储。"""
    conn = _get_conn()
    try:
        _init_db(conn)
        now = datetime.utcnow().isoformat() + "Z"
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, ensure_ascii=False), now),
        )
        conn.commit()
    finally:
        conn.close()


def get_all() -> dict[str, Any]:
    """读取所有配置，返回 { key: 解析后的 value }。"""
    conn = _get_conn()
    try:
        _init_db(conn)
        rows = conn.execute("SELECT key, value FROM config").fetchall()
        out: dict[str, Any] = {}
        for row in rows:
            out[row["key"]] = json.loads(row["value"])
        return out
    finally:
        conn.close()


def set_many(updates: dict[str, Any]) -> None:
    """批量写入配置。"""
    if not updates:
        return
    conn = _get_conn()
    try:
        _init_db(conn)
        now = datetime.utcnow().isoformat() + "Z"
        conn.executemany(
            "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
            [(k, json.dumps(v, ensure_ascii=False), now) for k, v in updates.items()],
        )
        conn.commit()
    finally:
        conn.close()


# 配置命名空间：前端可扩展
CONFIG_KEY_MODEL = "model"  # 模型相关（默认模型、参数等）
CONFIG_KEY_UI = "ui"        # 界面设置（主题、布局等）


def get_default_model_config() -> dict[str, Any]:
    """返回默认模型配置结构。各模态下 models 为「模型 id -> 参数」便于前端按模型单独配置。"""
    return {
        "text": {
            "default_model": "GLM-5",
            "params": {},
            "models": {"GLM-5": {"params": {}}},
        },
        "image": {
            "default_model": "Doubao-Seedream-4.5",
            "params": {},
            "models": {"Doubao-Seedream-4.5": {"params": {}}},
        },
        "video": {
            "default_model": "即梦视频生成 3.0 Pro",
            "params": {"aspect_ratio": "16:9", "seconds": 5},
            "models": {"即梦视频生成 3.0 Pro": {"params": {"aspect_ratio": "16:9", "seconds": 5}}},
        },
    }


def get_default_ui_config() -> dict[str, Any]:
    """返回默认界面配置结构。"""
    return {
        "theme": "dark",
        "sidebar_collapsed": False,
    }
