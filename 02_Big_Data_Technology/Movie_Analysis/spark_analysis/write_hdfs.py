# -*- coding: utf-8 -*-
"""HDFS 写入模块 — 将 Spark DataFrame 分析结果写入 HDFS"""

import os
from pyspark.sql import SparkSession, DataFrame
from config import HDFS_CONFIG

OUTPUT_BASE = HDFS_CONFIG["output_base"]
FORMAT = HDFS_CONFIG["format"]  # parquet (推荐) / csv / json


def _hdfs_path(name: str) -> str:
    """组装 HDFS 输出路径。"""
    return os.path.join(OUTPUT_BASE, name)


def _write_to_hdfs(df: DataFrame, name: str, mode: str = "overwrite"):
    """通用 HDFS 写入辅助函数。"""
    path = _hdfs_path(name)
    if FORMAT == "parquet":
        df.write.mode(mode).parquet(path)
    elif FORMAT == "csv":
        df.write.mode(mode).option("header", "true").csv(path)
    elif FORMAT == "json":
        df.write.mode(mode).json(path)
    else:
        raise ValueError(f"不支持的 HDFS 输出格式: {FORMAT}")
    print(f"  ✓ {name} → {path}")


def write_movie_stats(df: DataFrame):
    _write_to_hdfs(df, "movie_stats")


def write_genre_stats(df: DataFrame):
    _write_to_hdfs(df, "genre_stats")


def write_rating_distribution(df: DataFrame):
    _write_to_hdfs(df, "rating_distribution")


def write_top10_movies(df: DataFrame):
    _write_to_hdfs(df, "top10_movies")


def write_female_top10(df: DataFrame):
    _write_to_hdfs(df, "female_18_24_top10")


def write_male_genre_top3(df: DataFrame):
    _write_to_hdfs(df, "male_25_34_genre_top3")


def write_user_activity(df: DataFrame):
    _write_to_hdfs(df, "user_activity")


def write_all_to_hdfs(results: dict):
    """将分析结果一键写入 HDFS。

    Args:
        results: run_all_analyses() 返回的 {名称: DataFrame} 字典
    """
    print("\n" + "=" * 60)
    print(f"  写入 HDFS （格式: {FORMAT}）...")
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

    print("\n  HDFS 写入完成。")
