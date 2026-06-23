# -*- coding: utf-8 -*-
"""Spark 电影分析项目 — 配置模块"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "ml-1m")

# ================================================================
# 数据文件路径
# ================================================================
MOVIES_FILE = os.path.join(DATA_DIR, "movies.dat")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.dat")
USERS_FILE = os.path.join(DATA_DIR, "users.dat")

# ================================================================
# MySQL 配置
# ================================================================
MYSQL_CONFIG = {
    "url": "jdbc:mysql://localhost:3306/movie_analysis",
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "root",
    "password": "root",
    "tables": {
        "movie_stats": "movie_stats",
        "genre_stats": "genre_stats",
        "rating_distribution": "rating_distribution",
        "top10_movies": "top10_movies",
        "female_top10": "female_top10",
        "male_genre_top3": "male_genre_top3",
        "demographic_analysis": "demographic_analysis",
        "user_activity": "user_activity",
    },
}

# ================================================================
# HDFS 配置（根据实际集群调整）
# ================================================================
HDFS_CONFIG = {
    "output_base": "hdfs://localhost:9000/user/spark/movie_analysis",
    "format": "parquet",  # parquet / csv / json
}
