# -*- coding: utf-8 -*-
"""MySQL 写入模块 — 将 Spark DataFrame 分析结果写入 MySQL 数据库"""

from pyspark.sql import SparkSession, DataFrame
from config import MYSQL_CONFIG

URL = MYSQL_CONFIG["url"]
DRIVER = MYSQL_CONFIG["driver"]
USER = MYSQL_CONFIG["user"]
PASSWORD = MYSQL_CONFIG["password"]
TABLES = MYSQL_CONFIG["tables"]


def _jdbc_props() -> dict:
    return {
        "driver": DRIVER,
        "user": USER,
        "password": PASSWORD,
    }


def _write_table(df: DataFrame, table_name: str, mode: str = "overwrite"):
    """通用写入 MySQL 表的辅助函数。"""
    df.write.jdbc(
        url=URL,
        table=table_name,
        mode=mode,
        properties=_jdbc_props(),
    )


def write_movie_stats(df: DataFrame):
    """写电影评分统计表。"""
    _write_table(df, TABLES["movie_stats"])
    print(f"  ✓ movie_stats → MySQL ({df.count()} 行)")


def write_genre_stats(df: DataFrame):
    """写电影类型统计表。"""
    _write_table(df, TABLES["genre_stats"])
    print(f"  ✓ genre_stats → MySQL ({df.count()} 行)")


def write_rating_distribution(df: DataFrame):
    """写评分分布表。"""
    _write_table(df, TABLES["rating_distribution"])
    print(f"  ✓ rating_distribution → MySQL ({df.count()} 行)")


def write_top10_movies(df: DataFrame):
    """写 Top10 电影表。"""
    _write_table(df, TABLES["top10_movies"])
    print(f"  ✓ top10_movies → MySQL ({df.count()} 行)")


def write_female_top10(df: DataFrame):
    """写 18-24 女性 Top10。"""
    _write_table(df, TABLES["female_top10"])
    print(f"  ✓ female_top10 → MySQL ({df.count()} 行)")


def write_male_genre_top3(df: DataFrame):
    """写 25-34 男性 Top3 类型。"""
    _write_table(df, TABLES["male_genre_top3"])
    print(f"  ✓ male_genre_top3 → MySQL ({df.count()} 行)")


def write_demographic_analysis(df: DataFrame):
    """写人口画像分析（年龄段 + 性别）。"""
    _write_table(df, TABLES["demographic_analysis"])
    print(f"  ✓ demographic_analysis → MySQL ({df.count()} 行)")


def write_user_activity(df: DataFrame):
    """写用户活跃度分析。"""
    _write_table(df, TABLES["user_activity"])
    print(f"  ✓ user_activity → MySQL ({df.count()} 行)")


def write_all_to_mysql(results: dict):
    """将分析结果一键写入 MySQL。

    Args:
        results: run_all_analyses() 返回的 {名称: DataFrame} 字典
    """
    print("\n" + "=" * 60)
    print("  写入 MySQL ...")
    print("=" * 60)

    mapping = [
        ("movie_stats", write_movie_stats),
        ("genre_stats", write_genre_stats),
        ("rating_distribution", write_rating_distribution),
        ("top10_movies", write_top10_movies),
        ("female_18_24_top10", write_female_top10),
        ("male_25_34_genre_top3", write_male_genre_top3),
        ("user_activity", write_user_activity),
    ]

    for key, fn in mapping:
        if key in results:
            fn(results[key])
        else:
            print(f"  ⚠ 跳过 {key}（结果中不存在）")

    print("\n  MySQL 写入完成。")
