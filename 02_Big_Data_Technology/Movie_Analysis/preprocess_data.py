#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""预处理 MovieLens 1M 数据集，生成用于Web展示的JSON数据"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "ml-1m")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# 年龄映射
AGE_MAP = {
    1: "Under 18",
    18: "18-24",
    25: "25-34",
    35: "35-44",
    45: "45-49",
    50: "50-55",
    56: "56+"
}

# 职业映射
OCCUPATION_MAP = {
    0: "other",
    1: "academic/educator",
    2: "artist",
    3: "clerical/admin",
    4: "college/grad student",
    5: "customer service",
    6: "doctor/health care",
    7: "executive/managerial",
    8: "farmer",
    9: "homemaker",
    10: "K-12 student",
    11: "lawyer",
    12: "programmer",
    13: "retired",
    14: "sales/marketing",
    15: "scientist",
    16: "self-employed",
    17: "technician/engineer",
    18: "tradesman/craftsman",
    19: "unemployed",
    20: "writer"
}

print("Step 1: Loading movies...")
movies = {}
with open(os.path.join(DATA_DIR, "movies.dat"), "r", encoding="ISO-8859-1") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("::")
        movie_id = int(parts[0])
        title = parts[1]
        genres = parts[2].split("|")
        movies[movie_id] = {"id": movie_id, "title": title, "genres": genres}

print(f"  Loaded {len(movies)} movies")

print("Step 2: Loading users...")
users = {}
with open(os.path.join(DATA_DIR, "users.dat"), "r", encoding="ISO-8859-1") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("::")
        uid = int(parts[0])
        gender = parts[1]
        age_code = int(parts[2])
        occupation_code = int(parts[3])
        users[uid] = {
            "id": uid,
            "gender": gender,
            "age_group": AGE_MAP.get(age_code, str(age_code)),
            "age_code": age_code,
            "occupation": OCCUPATION_MAP.get(occupation_code, str(occupation_code))
        }

print(f"  Loaded {len(users)} users")

print("Step 3: Loading ratings and computing stats...")
# 电影评分统计
movie_ratings = {}  # movie_id -> [ratings list]
user_ratings = {}   # user_id -> [(movie_id, rating)]
genre_ratings = {}  # genre -> [ratings list]

with open(os.path.join(DATA_DIR, "ratings.dat"), "r", encoding="ISO-8859-1") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("::")
        uid = int(parts[0])
        mid = int(parts[1])
        rating = float(parts[2])
        ts = int(parts[3])

        # 按电影统计
        if mid not in movie_ratings:
            movie_ratings[mid] = []
        movie_ratings[mid].append(rating)

        # 按用户统计
        if uid not in user_ratings:
            user_ratings[uid] = []
        user_ratings[uid].append((mid, rating))

        # 按类型统计
        if mid in movies:
            for genre in movies[mid]["genres"]:
                if genre not in genre_ratings:
                    genre_ratings[genre] = []
                genre_ratings[genre].append(rating)

print(f"  Loaded ratings for {len(movie_ratings)} movies, {len(user_ratings)} users")

print("Step 4: Computing movie statistics...")
movie_stats_list = []
for mid, ratings in movie_ratings.items():
    cnt = len(ratings)
    avg = sum(ratings) / cnt
    movie_info = movies.get(mid, {"title": f"Movie {mid}", "genres": ["Unknown"]})
    movie_stats_list.append({
        "movieId": mid,
        "title": movie_info["title"],
        "genres": movie_info["genres"],
        "avgRating": round(avg, 2),
        "cntRating": cnt
    })

# 按评分次数排序
movie_stats_list.sort(key=lambda x: x["cntRating"], reverse=True)

# Top10 电影（评分次数 > 2000，平均评分最高）
top10_movies = [m for m in movie_stats_list if m["cntRating"] >= 2000]
top10_movies.sort(key=lambda x: (-x["avgRating"], -x["cntRating"]))
top10_movies = top10_movies[:10]

print(f"\n=== Top 10 Movies (ratings >= 2000) ===")
for i, m in enumerate(top10_movies):
    print(f"  {i+1}. [{m['movieId']}] {m['title']} - Avg: {m['avgRating']}, Count: {m['cntRating']}")

print("\nStep 5: Computing genre statistics...")
genre_stats = {}
for genre, ratings in genre_ratings.items():
    cnt = len(ratings)
    avg = sum(ratings) / cnt
    genre_stats[genre] = {
        "genre": genre,
        "avgRating": round(avg, 2),
        "cntRating": cnt
    }
genre_list = sorted(genre_stats.values(), key=lambda x: x["cntRating"], reverse=True)

print("\nStep 6: Computing demographic analysis...")

# 程序设计二: 18-24女性用户评分最高的10部电影
female_18_24_users = [uid for uid, u in users.items() if u["gender"] == "F" and u["age_group"] == "18-24"]
print(f"  Female 18-24 users: {len(female_18_24_users)}")

female_movie_ratings = {}  # movie_id -> [ratings]
for uid in female_18_24_users:
    if uid in user_ratings:
        for mid, rating in user_ratings[uid]:
            if mid not in female_movie_ratings:
                female_movie_ratings[mid] = []
            female_movie_ratings[mid].append(rating)

female_top10 = []
for mid, ratings in female_movie_ratings.items():
    cnt = len(ratings)
    avg = sum(ratings) / cnt
    movie_info = movies.get(mid, {"title": f"Movie {mid}", "genres": ["Unknown"]})
    female_top10.append({
        "movieId": mid,
        "title": movie_info["title"],
        "genres": movie_info["genres"],
        "avgRating": round(avg, 2),
        "cntRating": cnt
    })

female_top10.sort(key=lambda x: (-x["avgRating"], -x["cntRating"]))
female_top10 = female_top10[:10]

print(f"\n=== Top 10 Movies for Female 18-24 ===")
for i, m in enumerate(female_top10):
    print(f"  {i+1}. [{m['movieId']}] {m['title']} - Avg: {m['avgRating']}, Count: {m['cntRating']}")

# 程序设计二: 25-34男性用户最喜欢的3种电影类型
male_25_34_users = [uid for uid, u in users.items() if u["gender"] == "M" and u["age_group"] == "25-34"]
print(f"\n  Male 25-34 users: {len(male_25_34_users)}")

male_genre_ratings = {}
for uid in male_25_34_users:
    if uid in user_ratings:
        for mid, rating in user_ratings[uid]:
            if mid in movies:
                for genre in movies[mid]["genres"]:
                    if genre not in male_genre_ratings:
                        male_genre_ratings[genre] = []
                    male_genre_ratings[genre].append(rating)

male_genre_top = []
for genre, ratings in male_genre_ratings.items():
    cnt = len(ratings)
    avg = sum(ratings) / cnt
    male_genre_top.append({
        "genre": genre,
        "avgRating": round(avg, 2),
        "cntRating": cnt
    })

male_genre_top.sort(key=lambda x: (-x["avgRating"], -x["cntRating"]))
male_genre_top3 = male_genre_top[:3]

print(f"\n=== Top 3 Genres for Male 25-34 ===")
for i, g in enumerate(male_genre_top3):
    print(f"  {i+1}. {g['genre']} - Avg: {g['avgRating']}, Count: {g['cntRating']}")

print("\nStep 7: Computing rating distribution...")
# 评分分布
rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
total_ratings = 0
for ratings in movie_ratings.values():
    for r in ratings:
        rating_dist[int(r)] = rating_dist.get(int(r), 0) + 1
        total_ratings += 1

print(f"  Total ratings: {total_ratings}")
for k in sorted(rating_dist.keys()):
    print(f"    {k} stars: {rating_dist[k]} ({rating_dist[k]/total_ratings*100:.1f}%)")

print("\nStep 8: Saving all data to JSON...")

# 只保存前200条电影统计用于前端展示（全部数据太大）
output = {
    "totalMovies": len(movies),
    "totalUsers": len(users),
    "totalRatings": total_ratings,
    "top10Movies": top10_movies,
    "movieStats": movie_stats_list[:500],  # top 500 by rating count
    "genreStats": genre_list,
    "femaleTop10": female_top10,
    "maleGenreTop3": male_genre_top3,
    "ratingDistribution": [{"rating": k, "count": v} for k, v in sorted(rating_dist.items())],
    "allGenres": [g["genre"] for g in genre_list]
}

with open(os.path.join(STATIC_DIR, "data.json"), "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False)

# 保存完整电影列表用于搜索
all_movies = []
for mid, info in movies.items():
    all_movies.append(info)
with open(os.path.join(STATIC_DIR, "movies.json"), "w", encoding="utf-8") as f:
    json.dump(all_movies, f, ensure_ascii=False)

# 保存全部评分统计
with open(os.path.join(STATIC_DIR, "movie_stats_full.json"), "w", encoding="utf-8") as f:
    json.dump(movie_stats_list, f, ensure_ascii=False)

print("\nDone! All data saved to static/ directory.")
