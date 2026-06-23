#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MovieLens 电影用户爱好分析 Web API"""

import json
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 加载数据
with open(os.path.join(STATIC_DIR, "data.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

with open(os.path.join(STATIC_DIR, "movies.json"), "r", encoding="utf-8") as f:
    all_movies = json.load(f)

with open(os.path.join(STATIC_DIR, "movie_stats_full.json"), "r", encoding="utf-8") as f:
    movie_stats_full = json.load(f)

# 构建索引
movie_by_id = {m["id"]: m for m in all_movies}
movie_stats_by_id = {m["movieId"]: m for m in movie_stats_full}

# 所有类型
all_genres = data["allGenres"]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/summary")
def summary():
    """返回数据集概览"""
    return jsonify({
        "totalMovies": data["totalMovies"],
        "totalUsers": data["totalUsers"],
        "totalRatings": data["totalRatings"],
        "genres": all_genres
    })

@app.route("/api/top10")
def top10():
    """返回 Top10 电影（评分次数 > 2000）"""
    return jsonify(data["top10Movies"])

@app.route("/api/female_top10")
def female_top10():
    """返回 18-24 女性用户评分最高的 10 部电影"""
    return jsonify(data["femaleTop10"])

@app.route("/api/male_genre_top3")
def male_genre_top3():
    """返回 25-34 男性用户最喜欢的 3 种电影类型"""
    return jsonify(data["maleGenreTop3"])

@app.route("/api/genre_stats")
def genre_stats():
    """返回各类型电影统计"""
    return jsonify(data["genreStats"])

@app.route("/api/rating_distribution")
def rating_distribution():
    """返回评分分布"""
    return jsonify(data["ratingDistribution"])

@app.route("/api/movies")
def search_movies():
    """搜索和筛选电影"""
    query = request.args.get("q", "").lower()
    genre = request.args.get("genre", "")
    min_rating = request.args.get("min_rating", 0, type=float)
    max_rating = request.args.get("max_rating", 5, type=float)
    min_count = request.args.get("min_count", 0, type=int)
    sort_by = request.args.get("sort_by", "cntRating")  # avgRating or cntRating
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    results = []
    for m in movie_stats_full:
        # 搜索关键词
        if query:
            title_lower = m["title"].lower()
            if query not in title_lower:
                continue

        # 类型筛选
        if genre:
            if genre not in m["genres"]:
                continue

        # 评分范围
        if m["avgRating"] < min_rating or m["avgRating"] > max_rating:
            continue

        # 最少评分次数
        if m["cntRating"] < min_count:
            continue

        results.append(m)

    # 排序
    if sort_by == "avgRating":
        results.sort(key=lambda x: (-x["avgRating"], -x["cntRating"]))
    else:
        results.sort(key=lambda x: (-x["cntRating"], -x["avgRating"]))

    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = results[start:end]

    return jsonify({
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "data": page_data
    })

@app.route("/api/movie/<int:movie_id>")
def movie_detail(movie_id):
    """获取电影详情"""
    movie = movie_by_id.get(movie_id)
    stats = movie_stats_by_id.get(movie_id)
    if not stats:
        return jsonify({"error": "Movie not found"}), 404

    return jsonify({
        "id": movie_id,
        "title": movie["title"] if movie else stats["title"],
        "genres": movie["genres"] if movie else stats["genres"],
        "avgRating": stats["avgRating"],
        "cntRating": stats["cntRating"]
    })

@app.route("/api/genres")
def genres():
    """返回所有电影类型"""
    return jsonify(all_genres)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
