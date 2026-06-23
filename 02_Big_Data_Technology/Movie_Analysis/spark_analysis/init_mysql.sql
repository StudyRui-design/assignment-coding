-- ================================================================
-- MovieLens 分析结果 — MySQL 建表脚本
-- 在首次运行 Spark 分析任务前执行
-- ================================================================

CREATE DATABASE IF NOT EXISTS movie_analysis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE movie_analysis;

-- 1. 电影评分统计
DROP TABLE IF EXISTS movie_stats;
CREATE TABLE movie_stats (
    movieId        INT           NOT NULL PRIMARY KEY,
    title          VARCHAR(255)  NOT NULL,
    genres         VARCHAR(255),
    avg_rating     DECIMAL(5,3),
    cnt_rating     INT,
    std_rating     DECIMAL(5,3),
    pct_high_rating DECIMAL(5,1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 类型统计
DROP TABLE IF EXISTS genre_stats;
CREATE TABLE genre_stats (
    genre          VARCHAR(50)   NOT NULL PRIMARY KEY,
    cnt_rating     INT,
    avg_rating     DECIMAL(5,3),
    std_rating     DECIMAL(5,3),
    pct_high_rating DECIMAL(5,1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 评分分布
DROP TABLE IF EXISTS rating_distribution;
CREATE TABLE rating_distribution (
    rating         INT           NOT NULL PRIMARY KEY,
    cnt            INT,
    pct            DECIMAL(5,1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Top10 高分电影
DROP TABLE IF EXISTS top10_movies;
CREATE TABLE top10_movies (
    movieId        INT           NOT NULL PRIMARY KEY,
    title          VARCHAR(255),
    genres         VARCHAR(255),
    avg_rating     DECIMAL(5,3),
    cnt_rating     INT,
    std_rating     DECIMAL(5,3),
    pct_high_rating DECIMAL(5,1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 18-24 女性 Top10
DROP TABLE IF EXISTS female_top10;
CREATE TABLE female_top10 (
    movieId        INT           NOT NULL PRIMARY KEY,
    title          VARCHAR(255),
    genres         VARCHAR(255),
    avg_rating     DECIMAL(5,3),
    cnt            INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 25-34 男性 Top3 类型
DROP TABLE IF EXISTS male_genre_top3;
CREATE TABLE male_genre_top3 (
    genre          VARCHAR(50)   NOT NULL PRIMARY KEY,
    cnt_rating     INT,
    avg_rating     DECIMAL(5,3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 人口画像分析
DROP TABLE IF EXISTS demographic_analysis;
CREATE TABLE demographic_analysis (
    group_key      VARCHAR(50)   NOT NULL PRIMARY KEY,
    user_cnt       INT,
    rating_cnt     INT,
    avg_rating     DECIMAL(5,3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 用户活跃度
DROP TABLE IF EXISTS user_activity;
CREATE TABLE user_activity (
    activity_level VARCHAR(50)   NOT NULL PRIMARY KEY,
    user_cnt       INT,
    avg_rating     DECIMAL(5,3),
    avg_rating_count DECIMAL(10,1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
