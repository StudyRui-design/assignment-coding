# -*- coding: utf-8 -*-
"""Spark 数据加载模块 — 同时支持 RDD 与 DataFrame/SQL 两种模式"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField, IntegerType, FloatType, StringType, LongType,
)
from pyspark.rdd import RDD
from config import MOVIES_FILE, RATINGS_FILE, USERS_FILE


def create_spark_session(app_name: str = "MovieLens_Analysis") -> SparkSession:
    """创建并返回 SparkSession，启用 Hive 支持以便写入 HDFS 表。"""
    spark = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .enableHiveSupport()
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


# ================================================================
# 方式一：RDD 加载（底层 map/filter 操作）
# ================================================================

def load_movies_rdd(spark: SparkSession) -> RDD:
    """RDD 方式加载 movies.dat → (movieId, (title, year, [genres]))"""
    sc = spark.sparkContext
    raw = sc.textFile(MOVIES_FILE)

    def parse_movie(line: str):
        parts = line.strip().split("::")
        if len(parts) < 3:
            return None
        movie_id = int(parts[0])
        title_with_year = parts[1]
        genres = parts[2].split("|")
        # 提取年份
        year = None
        if title_with_year.endswith(")") and "(" in title_with_year:
            year_str = title_with_year[title_with_year.rindex("(") + 1 : -1]
            try:
                year = int(year_str)
            except ValueError:
                pass
        return (movie_id, (title_with_year, year, genres))

    return raw.map(parse_movie).filter(lambda x: x is not None)


def load_ratings_rdd(spark: SparkSession) -> RDD:
    """RDD 方式加载 ratings.dat → (userId, movieId, rating, timestamp)"""
    sc = spark.sparkContext
    raw = sc.textFile(RATINGS_FILE)

    def parse_rating(line: str):
        parts = line.strip().split("::")
        if len(parts) < 4:
            return None
        return (
            int(parts[0]),
            int(parts[1]),
            float(parts[2]),
            int(parts[3]),
        )

    return raw.map(parse_rating).filter(lambda x: x is not None)


def load_users_rdd(spark: SparkSession) -> RDD:
    """RDD 方式加载 users.dat → (userId, (gender, age, occupation, zip))"""
    sc = spark.sparkContext
    raw = sc.textFile(USERS_FILE)

    AGE_MAP = {1: 7, 18: 18, 25: 25, 35: 35, 45: 45, 50: 50, 56: 56}

    def parse_user(line: str):
        parts = line.strip().split("::")
        if len(parts) < 4:
            return None
        uid = int(parts[0])
        gender = parts[1]
        age_code = int(parts[2])
        age_label = AGE_MAP.get(age_code, age_code)
        occupation = int(parts[3])
        zip_code = parts[4] if len(parts) > 4 else ""
        return (uid, (gender, age_label, occupation, zip_code))

    return raw.map(parse_user).filter(lambda x: x is not None)


# ================================================================
# 方式二：DataFrame 加载（声明式 Schema，可直接注册为 SQL 表）
# ================================================================

def load_movies_df(spark: SparkSession) -> DataFrame:
    """DataFrame 方式加载 movies.dat，解析 genres 为数组列。"""
    movies = (
        spark.read.option("delimiter", "::")
        .option("inferSchema", "false")
        .csv(MOVIES_FILE)
        .toDF("movieId", "title", "genres_raw")
    )
    movies.createOrReplaceTempView("movies")
    return movies


def load_ratings_df(spark: SparkSession) -> DataFrame:
    """DataFrame 方式加载 ratings.dat。"""
    schema = StructType(
        [
            StructField("userId", IntegerType(), True),
            StructField("movieId", IntegerType(), True),
            StructField("rating", FloatType(), True),
            StructField("timestamp", LongType(), True),
        ]
    )
    ratings = (
        spark.read.option("delimiter", "::")
        .schema(schema)
        .csv(RATINGS_FILE)
    )
    ratings.createOrReplaceTempView("ratings")
    return ratings


def load_users_df(spark: SparkSession) -> DataFrame:
    """DataFrame 方式加载 users.dat。"""
    schema = StructType(
        [
            StructField("userId", IntegerType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("occupation", IntegerType(), True),
            StructField("zipCode", StringType(), True),
        ]
    )
    users = (
        spark.read.option("delimiter", "::")
        .schema(schema)
        .csv(USERS_FILE)
    )
    users.createOrReplaceTempView("users")
    return users


def register_all_tables(spark: SparkSession):
    """一键加载三张表并注册为 SQL 临时视图。

    注册后可以直接用 SQL 查询：
      SELECT * FROM movies
      SELECT * FROM ratings
      SELECT * FROM users
    """
    load_movies_df(spark)
    load_ratings_df(spark)
    load_users_df(spark)
