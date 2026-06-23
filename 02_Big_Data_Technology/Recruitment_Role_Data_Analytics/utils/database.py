# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics - 数据库工具模块
提供连接上下文管理器，避免资源泄漏
"""
import threading
import time
from contextlib import contextmanager

import pymysql
import pandas as pd

from config import DB_CONFIG

# ============================================================
# 连接上下文管理器
# ============================================================
@contextmanager
def get_connection():
    """
    安全的数据库连接上下文管理器
    用法:
        with get_connection() as conn:
            df = pd.read_sql("SELECT ...", conn)
    """
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def get_cursor():
    """
    获取游标的上下文管理器
    用法:
        with get_cursor() as cursor:
            cursor.execute(...)
    """
    conn = pymysql.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ============================================================
# 带缓存的 DataFrame 查询（供 Web API 使用）
# ============================================================
_cache = {"df": None, "ts": 0, "lock": threading.Lock()}
_CACHE_TTL = 3  # 秒，覆盖单次页面加载的所有API请求


def get_dataframe(force_refresh: bool = False) -> pd.DataFrame:
    """
    从数据库加载全表 DataFrame，带短时缓存

    参数:
        force_refresh: 是否跳过缓存强制刷新
    返回:
        pd.DataFrame (copy)
    """
    now = time.time()
    with _cache["lock"]:
        if not force_refresh and _cache["df"] is not None and (now - _cache["ts"]) < _CACHE_TTL:
            return _cache["df"].copy()

    with get_connection() as conn:
        df = pd.read_sql("SELECT * FROM t_recruitment_info", conn)

    with _cache["lock"]:
        _cache["df"] = df.copy()
        _cache["ts"] = time.time()
    return df
