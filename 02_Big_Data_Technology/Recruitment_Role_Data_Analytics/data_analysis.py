# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics
基于 recruitment_db.t_recruitment_info 表，完成8项分析并输出图片到 ./static/images/
"""

import os
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from wordcloud import WordCloud

from config import DB_CONFIG, COLORS, OUTPUT_DIR
from utils import register_benefits_dict, BENEFITS_CUSTOM_WORDS, BENEFITS_STOPWORDS
from utils.database import get_connection

warnings.filterwarnings("ignore")

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 中文字体设置
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"]
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["figure.dpi"] = 120


def save_fig(fig, name):
    """保存图表到输出目录"""
    path = OUTPUT_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"  [OK] {name}")


# ============================================================
# 读取数据
# ============================================================
def load_data():
    with get_connection() as conn:
        df = pd.read_sql("SELECT * FROM t_recruitment_info", conn)
    print(f"[数据] 读取 {len(df)} 条记录")
    return df


# ============================================================
# 1. 城市岗位数量占比（饼图 + 柱状图）
# ============================================================
def analysis_city_distribution(df):
    print("\n[分析1] 城市岗位数量占比")
    city_counts = df["city"].value_counts()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # 左侧：饼图
    wedges, texts, autotexts = axes[0].pie(
        city_counts.values,
        labels=city_counts.index,
        autopct="%1.1f%%",
        colors=COLORS[:len(city_counts)],
        startangle=90,
        pctdistance=0.75,
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_color("white")
        t.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(11)
    axes[0].set_title("城市岗位数量占比（饼图）", fontsize=14, fontweight="bold", pad=15)

    # 右侧：柱状图
    bars = axes[1].bar(city_counts.index, city_counts.values, color=COLORS[:len(city_counts)], width=0.5)
    axes[1].set_title("城市岗位数量分布（柱状图）", fontsize=14, fontweight="bold", pad=15)
    axes[1].set_xlabel("城市", fontsize=11)
    axes[1].set_ylabel("岗位数量（条）", fontsize=11)
    for bar, val in zip(bars, city_counts.values):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")
    axes[1].set_ylim(0, max(city_counts.values) * 1.18)
    axes[1].yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    save_fig(fig, "01_city_distribution.png")
    print(f"  城市分布: {city_counts.to_dict()}")


# ============================================================
# 2. 学历要求分布（饼图）
# ============================================================
def analysis_education_distribution(df):
    print("\n[分析2] 学历要求分布")
    # 仅统计非空真实数据
    df_real = df[df["education"].notna() & (df["education"] != "")]
    if len(df_real) == 0:
        print(f"  [跳过] education字段均未采集到真实数据")
        return
    edu_counts = df_real["education"].value_counts()

    # 定义学历排序
    edu_order = ["博士", "硕士", "本科", "大专", "不限"]
    edu_sorted = {k: edu_counts.get(k, 0) for k in edu_order if k in edu_counts.index}
    others = {k: v for k, v in edu_counts.items() if k not in edu_order}
    edu_sorted.update(others)

    fig, ax = plt.subplots(figsize=(8, 6))
    labels = list(edu_sorted.keys())
    values = list(edu_sorted.values())

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=COLORS[:len(labels)],
        startangle=140, pctdistance=0.6,
        explode=[0.03] * len(labels),
    )
    for t in autotexts:
        t.set_fontsize(11)
        t.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(12)
    ax.set_title("学历要求分布", fontsize=15, fontweight="bold", pad=18)

    save_fig(fig, "02_education_distribution.png")
    print(f"  学历分布: {edu_sorted}")


# ============================================================
# 3. 企业类型占比（饼图）
# ============================================================
def analysis_com_type_distribution(df):
    print("\n[分析3] 企业类型占比")
    type_counts = df["com_type"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 7))
    labels = type_counts.index.tolist()
    values = type_counts.values.tolist()

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=COLORS[:len(labels)],
        startangle=90, pctdistance=0.56,
        explode=[0.02] * len(labels),
        textprops={"fontsize": 11},
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("企业类型占比", fontsize=15, fontweight="bold", pad=18)

    save_fig(fig, "03_company_type.png")
    print(f"  企业类型: {type_counts.to_dict()}")


# ============================================================
# 4. 公司名称岗位数量排名 TOP10（横向条形图）
# ============================================================
def analysis_company_top10(df):
    print("\n[分析4] 公司岗位数量排名 TOP10")
    com_counts = df["com_name"].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(11, 6))
    companies = com_counts.index.tolist()[::-1]
    counts = com_counts.values.tolist()[::-1]
    bar_colors = COLORS[:10][::-1]

    bars = ax.barh(companies, counts, color=bar_colors, height=0.6)
    ax.set_title("公司岗位数量排名 TOP10", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("岗位数量（条）", fontsize=11)
    for bar, val in zip(bars, counts):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, max(counts) * 1.15)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.tick_params(axis="y", labelsize=11)

    save_fig(fig, "04_company_top10.png")
    print(f"  TOP10: {com_counts.to_dict()}")


# ============================================================
# 5. 工作经验与平均薪资关系（折线图）
# ============================================================
def analysis_workyear_salary(df):
    print("\n[分析5] 工作经验与平均薪资关系")

    # 定义经验排序
    exp_order = ["应届", "1-3年", "3-5年", "5-10年", "10年以上"]
    df_exp = df.copy()
    # 仅统计非空真实数据
    df_exp = df_exp[df_exp["work_year"].notna() & (df_exp["work_year"] != "")]
    if len(df_exp) == 0:
        print(f"  [跳过] work_year字段均未采集到真实数据")
        return
    df_exp["work_year"] = pd.Categorical(
        df_exp["work_year"], categories=exp_order, ordered=True
    )

    grouped = df_exp.groupby("work_year", observed=False).agg(
        avg_salary_lower=("salary_lower", "mean"),
        avg_salary_high=("salary_high", "mean"),
        count=("id", "count"),
    ).reset_index()
    grouped = grouped.dropna(subset=["work_year"])

    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    x = range(len(grouped))
    ax1.plot(x, grouped["avg_salary_lower"], "o-", color=COLORS[0],
             linewidth=2.5, markersize=8, label="平均最低薪资(K)")
    ax1.plot(x, grouped["avg_salary_high"], "s-", color=COLORS[1],
             linewidth=2.5, markersize=8, label="平均最高薪资(K)")
    # 填充区域
    ax1.fill_between(x, grouped["avg_salary_lower"], grouped["avg_salary_high"],
                     alpha=0.13, color=COLORS[0])

    for i, row in grouped.iterrows():
        ax1.annotate(f'{row["avg_salary_lower"]:.1f}K',
                     (i, row["avg_salary_lower"]),
                     textcoords="offset points", xytext=(0, -18),
                     ha="center", fontsize=8, color=COLORS[0])
        ax1.annotate(f'{row["avg_salary_high"]:.1f}K',
                     (i, row["avg_salary_high"]),
                     textcoords="offset points", xytext=(0, 12),
                     ha="center", fontsize=8, color=COLORS[1])

    ax1.set_xticks(x)
    ax1.set_xticklabels(grouped["work_year"], fontsize=11)
    ax1.set_ylabel("薪资 (K)", fontsize=11)
    ax1.set_title("工作经验与平均薪资关系", fontsize=15, fontweight="bold", pad=15)
    ax1.legend(loc="upper left", fontsize=10)
    ax1.grid(axis="y", alpha=0.3)

    # 右轴：岗位数量
    ax2 = ax1.twinx()
    ax2.bar(x, grouped["count"], alpha=0.2, color="gray", width=0.4)
    ax2.set_ylabel("岗位数量", fontsize=10, color="gray")
    ax2.tick_params(axis="y", colors="gray")

    save_fig(fig, "05_workyear_salary.png")
    print(f"  薪资关系: \n{grouped.to_string()}")


# ============================================================
# 6. 薪资区间分布（直方图，10K一档）
# ============================================================
def analysis_salary_distribution(df):
    print("\n[分析6] 薪资区间分布（直方图）")

    # 用平均薪资作为基准
    df_temp = df.copy()
    df_temp["avg_salary"] = (df_temp["salary_lower"] + df_temp["salary_high"]) / 2

    bins = list(range(0, int(df_temp["avg_salary"].max()) + 10, 10))
    labels = [f"{bins[i]}-{bins[i+1]}K" for i in range(len(bins) - 1)]

    df_temp["salary_bin"] = pd.cut(
        df_temp["avg_salary"], bins=bins, labels=labels, right=False
    )
    bin_counts = df_temp["salary_bin"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 5.5))
    bars = ax.bar(range(len(bin_counts)), bin_counts.values,
                  color=COLORS[0], width=0.65, edgecolor="white", linewidth=0.5)

    ax.set_xticks(range(len(bin_counts)))
    ax.set_xticklabels(bin_counts.index, rotation=35, ha="right", fontsize=10)
    ax.set_xlabel("薪资区间（取每个岗位最低-最高均值）", fontsize=11)
    ax.set_ylabel("岗位数量（条）", fontsize=11)
    ax.set_title("薪资区间分布（直方图·10K一档）", fontsize=15, fontweight="bold", pad=15)

    for bar, val in zip(bars, bin_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                str(val), ha="center", fontsize=9, fontweight="bold")
    ax.set_ylim(0, max(bin_counts.values) * 1.15)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    save_fig(fig, "06_salary_distribution.png")
    print(f"  薪资区间: {bin_counts.to_dict()}")


# ============================================================
# 7. 企业规模分布（柱状图）— 替代原融资阶段分布
# ============================================================
def analysis_com_size(df):
    print("\n[分析7] 企业规模分布（基于真实com_size数据）")
    df_real = df[df["com_size"].notna() & (df["com_size"] != "")]
    if len(df_real) == 0:
        print(f"  [跳过] com_size字段均未采集到真实数据")
        return
    size_counts = df_real["com_size"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = list(size_counts.keys())
    values = list(size_counts.values)

    bars = ax.bar(range(len(labels)), values, color=COLORS[:len(labels)], width=0.55)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=10)
    ax.set_xlabel("企业规模", fontsize=11)
    ax.set_ylabel("岗位数量（条）", fontsize=11)
    ax.set_title("企业规模分布", fontsize=15, fontweight="bold", pad=15)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(val), ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.15)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    save_fig(fig, "07_com_size_distribution.png")
    print(f"  覆盖率: {len(df_real)}/{len(df)}, 企业规模: {size_counts.to_dict()}")


# ============================================================
# 8. 岗位福利词云图
# ============================================================
def analysis_benefits_wordcloud(df):
    print("\n[分析8] 岗位福利词云图（爬虫扩展版）")

    # 合并所有福利文本
    benefits_text = " ".join(df["job_benefits"].dropna().astype(str).tolist())

    # 使用共享福利关键词库
    import jieba
    from collections import Counter
    register_benefits_dict()

    segments = benefits_text.replace("/", " ").replace("、", " ").replace("，", " ").replace("+", " ")
    words = jieba.cut(segments)
    word_list = [w.strip() for w in words if len(w.strip()) >= 2]
    word_list = [w for w in word_list if w not in BENEFITS_STOPWORDS]

    word_freq = Counter(word_list)
    print(f"  词频TOP20: {word_freq.most_common(20)}")

    # 生成词云
    wc = WordCloud(
        font_path="C:/Windows/Fonts/msyh.ttc",
        width=1200,
        height=700,
        background_color="white",
        max_words=120,
        max_font_size=160,
        min_font_size=10,
        colormap="Set2",
        collocations=False,
        random_state=42,
        prefer_horizontal=0.7,
    )
    wc.generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("岗位福利词云（爬虫扩展版）", fontsize=20, fontweight="bold", pad=25)

    save_fig(fig, "08_benefits_wordcloud.png")


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 55)
    print("  Recruitment Role Data Analytics")
    print("=" * 55)

    df = load_data()

    analyses = [
        ("城市岗位数量占比", analysis_city_distribution),
        ("学历要求分布", analysis_education_distribution),
        ("企业类型占比", analysis_com_type_distribution),
        ("公司岗位排名TOP10", analysis_company_top10),
        ("工作经验与薪资关系", analysis_workyear_salary),
        ("薪资区间分布", analysis_salary_distribution),
        ("企业规模分布", analysis_com_size),
        ("岗位福利词云图", analysis_benefits_wordcloud),
    ]

    for name, func in analyses:
        try:
            func(df)
        except Exception as e:
            print(f"  [ERR] {name} 失败: {e}")
            import traceback
            traceback.print_exc()

    # 输出文件列表
    print(f"\n{'=' * 55}")
    print(f"  分析完成！图片保存至: {OUTPUT_DIR}")
    print(f"{'=' * 55}")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        size_kb = f.stat().st_size / 1024
        print(f"    {f.name}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
