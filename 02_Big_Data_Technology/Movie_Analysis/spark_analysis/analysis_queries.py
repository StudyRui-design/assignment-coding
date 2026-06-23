# -*- coding: utf-8 -*-
"""Spark SQL 电影分析查询模块

基于 MovieLens 1M 数据集，完成：
1. 电影评分统计分析（均值、计数、分布）
2. 多源数据关联查询（movies + ratings + users）
3. 按人群画像（年龄、性别、职业）交叉分析
"""

from pyspark.sql import SparkSession, DataFrame


# ================================================================
# 1. 数据集概览
# ================================================================

def dataset_summary(spark: SparkSession) -> DataFrame:
    """统计三张表的数据量：电影数、用户数、评分数。"""
    return spark.sql(
        """
        SELECT
            (SELECT COUNT(DISTINCT movieId) FROM movies)   AS total_movies,
            (SELECT COUNT(DISTINCT userId)  FROM users)    AS total_users,
            (SELECT COUNT(*)                FROM ratings)  AS total_ratings
        """
    )


# ================================================================
# 2. 电影评分统计
# ================================================================

def movie_rating_stats(spark: SparkSession, min_ratings: int = 50) -> DataFrame:
    """每部电影的评分均值、计数、标准差 — 过滤掉冷门电影。

    注册为视图 movie_stats，供后续查询复用。
    """
    df = spark.sql(
        f"""
        SELECT
            r.movieId,
            m.title,
            m.genres_raw                                 AS genres,
            ROUND(AVG(r.rating), 3)                      AS avg_rating,
            COUNT(*)                                      AS cnt_rating,
            ROUND(STDDEV(r.rating), 3)                    AS std_rating,
            ROUND(SUM(CASE WHEN r.rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_high_rating
        FROM ratings r
        JOIN movies m ON r.movieId = m.movieId
        GROUP BY r.movieId, m.title, m.genres_raw
        HAVING COUNT(*) >= {min_ratings}
        ORDER BY avg_rating DESC
        """
    )
    df.createOrReplaceTempView("movie_stats")
    return df


def top10_movies(spark: SparkSession) -> DataFrame:
    """Top10 高分电影 — 评分次数 >= 2000，按平均分降序。"""
    return spark.sql(
        """
        SELECT *
        FROM movie_stats
        WHERE cnt_rating >= 2000
        ORDER BY avg_rating DESC
        LIMIT 10
        """
    )


# ================================================================
# 3. 评分分布（1–5 星各占多少）
# ================================================================

def rating_distribution(spark: SparkSession) -> DataFrame:
    """评分 1-5 各级别的计数与占比。"""
    return spark.sql(
        """
        SELECT
            rating,
            COUNT(*)                                      AS cnt,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
        FROM ratings
        GROUP BY rating
        ORDER BY rating
        """
    )


# ================================================================
# 4. 电影类型分析
# ================================================================

def genre_stats(spark: SparkSession) -> DataFrame:
    """各类型电影的评分统计。

    注意：movies.genres_raw 是 "Action|Adventure" 格式，需要用 explode + split。
    """
    df = spark.sql(
        """
        WITH genre_exploded AS (
            SELECT
                r.rating,
                genre
            FROM ratings r
            JOIN movies m ON r.movieId = m.movieId
            LATERAL VIEW explode(split(m.genres_raw, '\\\\|')) t AS genre
        )
        SELECT
            genre,
            COUNT(*)                                      AS cnt_rating,
            ROUND(AVG(rating), 3)                         AS avg_rating,
            ROUND(STDDEV(rating), 3)                      AS std_rating,
            ROUND(SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_high_rating
        FROM genre_exploded
        GROUP BY genre
        ORDER BY cnt_rating DESC
        """
    )
    df.createOrReplaceTempView("genre_stats")
    return df


# ================================================================
# 5. 按用户性别分析
# ================================================================

def gender_analysis(spark: SparkSession) -> DataFrame:
    """按性别统计：用户数、平均评分、评分次数中位数。"""
    return spark.sql(
        """
        SELECT
            u.gender,
            COUNT(DISTINCT u.userId)                         AS user_cnt,
            COUNT(*)                                          AS rating_cnt,
            ROUND(AVG(r.rating), 3)                           AS avg_rating,
            ROUND(PERCENTILE(r.rating, 0.5), 2)              AS median_rating
        FROM ratings r
        JOIN users u ON r.userId = u.userId
        GROUP BY u.gender
        """
    )


# ================================================================
# 6. 按年龄段分析
# ================================================================

def age_group_analysis(spark: SparkSession) -> DataFrame:
    """按年龄段统计：各年龄段平均评分、评分次数、活跃用户数。"""
    return spark.sql(
        """
        SELECT
            u.age                             AS age_group,
            COUNT(DISTINCT u.userId)           AS user_cnt,
            COUNT(*)                           AS rating_cnt,
            ROUND(AVG(r.rating), 3)            AS avg_rating
        FROM ratings r
        JOIN users u ON r.userId = u.userId
        GROUP BY u.age
        ORDER BY u.age
        """
    )


# ================================================================
# 7. 人口画像交叉分析
# ================================================================

def female_18_24_top10(spark: SparkSession) -> DataFrame:
    """18-24 女性用户评分最高的 10 部电影。"""
    return spark.sql(
        """
        WITH target_ratings AS (
            SELECT r.movieId, r.rating
            FROM ratings r
            JOIN users u ON r.userId = u.userId
            WHERE u.gender = 'F' AND u.age = 18
        ),
        movie_agg AS (
            SELECT
                movieId,
                COUNT(*)                    AS cnt,
                ROUND(AVG(rating), 3)       AS avg_rating
            FROM target_ratings
            GROUP BY movieId
            HAVING COUNT(*) >= 20
        )
        SELECT
            m.movieId,
            m.title,
            m.genres_raw                   AS genres,
            a.avg_rating,
            a.cnt
        FROM movie_agg a
        JOIN movies m ON a.movieId = m.movieId
        ORDER BY a.avg_rating DESC
        LIMIT 10
        """
    )


def male_25_34_genre_top3(spark: SparkSession) -> DataFrame:
    """25-34 男性用户最喜欢的 3 种电影类型。"""
    return spark.sql(
        """
        WITH target_ratings AS (
            SELECT r.rating, genre
            FROM ratings r
            JOIN users u ON r.userId = u.userId
            JOIN movies m ON r.movieId = m.movieId
            LATERAL VIEW explode(split(m.genres_raw, '\\\\|')) t AS genre
            WHERE u.gender = 'M' AND u.age = 25
        )
        SELECT
            genre,
            COUNT(*)                     AS cnt_rating,
            ROUND(AVG(rating), 3)        AS avg_rating
        FROM target_ratings
        GROUP BY genre
        ORDER BY avg_rating DESC
        LIMIT 3
        """
    )


# ================================================================
# 8. 用户活跃度分析
# ================================================================

def user_activity(spark: SparkSession) -> DataFrame:
    """用户活跃度分档：高/中/低活跃用户的数量和平均评分。"""
    return spark.sql(
        """
        WITH user_stats AS (
            SELECT
                userId,
                COUNT(*)                  AS rating_cnt,
                ROUND(AVG(rating), 3)     AS avg_rating
            FROM ratings
            GROUP BY userId
        )
        SELECT
            CASE
                WHEN rating_cnt >= 500 THEN '高活跃 (>=500)'
                WHEN rating_cnt >= 100 THEN '中活跃 (100-499)'
                ELSE '低活跃 (<100)'
            END                          AS activity_level,
            COUNT(*)                      AS user_cnt,
            ROUND(AVG(avg_rating), 3)    AS avg_rating,
            ROUND(AVG(rating_cnt), 1)    AS avg_rating_count
        FROM user_stats
        GROUP BY
            CASE
                WHEN rating_cnt >= 500 THEN '高活跃 (>=500)'
                WHEN rating_cnt >= 100 THEN '中活跃 (100-499)'
                ELSE '低活跃 (<100)'
            END
        ORDER BY avg_rating_count DESC
        """
    )


# ================================================================
# 9. 关联查询：展示完整三板斧 join
# ================================================================

def full_join_sample(spark: SparkSession, limit: int = 20) -> DataFrame:
    """三表关联示例：映出评分 → 补充用户画像 + 电影标题。"""
    return spark.sql(
        f"""
        SELECT
            r.userId,
            u.gender,
            u.age,
            u.occupation,
            r.movieId,
            m.title,
            r.rating,
            FROM_UNIXTIME(r.timestamp) AS rating_time
        FROM ratings r
        JOIN users  u ON r.userId  = u.userId
        JOIN movies m ON r.movieId = m.movieId
        LIMIT {limit}
        """
    )


# ================================================================
# 10. 运行全部分析
# ================================================================

def run_all_analyses(spark: SparkSession) -> dict:
    """依次执行所有分析查询，返回 {名称: DataFrame} 字典。"""
    results = {}

    print("=" * 60)
    print("数据集概览")
    results["dataset_summary"] = dataset_summary(spark)

    print("=" * 60)
    print("电影评分统计 (min_ratings=50)")
    results["movie_stats"] = movie_rating_stats(spark, min_ratings=50)

    print("=" * 60)
    print("Top10 高分电影")
    results["top10_movies"] = top10_movies(spark)

    print("=" * 60)
    print("评分分布")
    results["rating_distribution"] = rating_distribution(spark)

    print("=" * 60)
    print("类型统计")
    results["genre_stats"] = genre_stats(spark)

    print("=" * 60)
    print("性别分析")
    results["gender_analysis"] = gender_analysis(spark)

    print("=" * 60)
    print("年龄段分析")
    results["age_group_analysis"] = age_group_analysis(spark)

    print("=" * 60)
    print("18-24 女性 Top10 电影")
    results["female_18_24_top10"] = female_18_24_top10(spark)

    print("=" * 60)
    print("25-34 男性 Top3 类型")
    results["male_25_34_genre_top3"] = male_25_34_genre_top3(spark)

    print("=" * 60)
    print("用户活跃度分析")
    results["user_activity"] = user_activity(spark)

    return results


def show_all(results: dict, n: int = 20):
    """打印所有分析结果到控制台。"""
    for name, df in results.items():
        print(f"\n{'=' * 60}")
        print(f"  {name}")
        print(f"{'=' * 60}")
        df.show(n, truncate=80)
