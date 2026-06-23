# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics - 机器学习预测模型
1. 决策树：预测热门城市（分类）
2. 线性回归：预测薪资
3. 随机森林：预测招聘强度（特征重要性）
模型保存至 ./models/ 目录
"""

import os
import sys
import pickle
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, r2_score, mean_squared_error
import matplotlib.pyplot as plt
import matplotlib

from config import DB_CONFIG, MODEL_DIR, RANDOM_STATE
from utils.database import get_connection

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False
warnings.filterwarnings("ignore")

# ============================================================
# 配置
# ============================================================
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    with get_connection() as conn:
        df = pd.read_sql("SELECT * FROM t_recruitment_info", conn)
    print(f"[数据] 读取 {len(df)} 条记录")
    return df


# ============================================================
# 1. 决策树：预测热门城市（分类任务）
# ============================================================
def model_decision_tree(df):
    print("\n" + "=" * 55)
    print("  模型1：决策树 —— 预测热门城市")
    print("=" * 55)

    # 特征与标签
    feature_cols = ["com_type", "com_size", "work_year", "education"]
    X_raw = df[feature_cols].copy()
    y_raw = df["city"].copy()

    # 移除空值（仅移除标签为空的，特征为空保留为空字符串）
    valid_mask = y_raw.notna()
    X_raw = X_raw[valid_mask]
    y_raw = y_raw[valid_mask]
    # 特征中空值填为"未知"
    for col in feature_cols:
        X_raw[col] = X_raw[col].fillna("未知").replace("", "未知")
    print(f"[数据] 有效样本: {len(X_raw)} 条")

    # LabelEncoder 编码所有分类特征
    encoders = {}
    X = X_raw.copy()
    for col in feature_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        print(f"  [编码] {col}: {len(le.classes_)} 类 -> {dict(zip(le.classes_, range(len(le.classes_))))}")

    # 标签编码
    y_le = LabelEncoder()
    y = y_le.fit_transform(y_raw)
    print(f"  [编码] city: {dict(zip(y_le.classes_, range(len(y_le.classes_))))}")

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    # 训练决策树（限制深度防止过拟合）
    dt = DecisionTreeClassifier(
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
    )
    dt.fit(X_train, y_train)

    # 预测评估
    y_pred = dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[评估] 测试集准确率: {acc:.2%}")

    # 交叉验证
    cv_scores = cross_val_score(dt, X, y, cv=5)
    print(f"[交叉验证] 5折平均准确率: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    print(f"\n[分类报告]")
    print(classification_report(y_test, y_pred, target_names=y_le.classes_, zero_division=0))

    # 特征重要性
    importance = pd.DataFrame({
        "特征": feature_cols,
        "重要性": dt.feature_importances_
    }).sort_values("重要性", ascending=False)
    print(f"\n[特征重要性]")
    for _, row in importance.iterrows():
        print(f"  {row['特征']}: {row['重要性']:.4f}")

    # 保存模型
    model_path = MODEL_DIR / "decision_tree_city.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": dt, "encoders": encoders, "label_encoder": y_le}, f)
    print(f"\n[保存] {model_path}")

    # 保存决策树可视化
    fig, ax = plt.subplots(figsize=(16, 8))
    plot_tree(dt, feature_names=feature_cols,
              class_names=y_le.classes_, filled=True, rounded=True,
              fontsize=9, ax=ax, impurity=False, proportion=True)
    ax.set_title("决策树：预测热门城市", fontsize=16, fontweight="bold")
    tree_path = MODEL_DIR / "decision_tree_visualization.png"
    fig.savefig(tree_path, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"[保存] 决策树可视化: {tree_path}")

    return dt, acc


# ============================================================
# 2. 线性回归：预测薪资
# ============================================================
def model_linear_regression(df):
    print("\n" + "=" * 55)
    print("  模型2：线性回归 —— 预测薪资")
    print("=" * 55)

    # 特征与标签
    feature_cols = ["city", "work_year", "education", "com_type", "com_size"]
    X_raw = df[feature_cols].copy()
    y_raw = ((df["salary_lower"] + df["salary_high"]) / 2).copy()

    # 移除空值（标签为空则移除；特征为空填"未知"）
    valid_mask = y_raw.notna()
    X_raw = X_raw[valid_mask]
    y_raw = y_raw[valid_mask]
    for col in feature_cols:
        X_raw[col] = X_raw[col].fillna("未知").replace("", "未知")
    print(f"[数据] 有效样本: {len(X_raw)} 条")
    print(f"[标签] 平均薪资范围: {y_raw.min():.1f}K ~ {y_raw.max():.1f}K, 均值: {y_raw.mean():.1f}K")

    # LabelEncoder 编码
    encoders = {}
    X = X_raw.copy()
    for col in feature_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        print(f"  [编码] {col}: {len(le.classes_)} 类")

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_raw, test_size=0.25, random_state=RANDOM_STATE
    )

    # 训练线性回归
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    # 预测评估
    y_pred = lr.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(f"\n[评估] R2: {r2:.4f}")
    print(f"[评估] MSE: {mse:.2f}, RMSE: {rmse:.2f}K")

    # 交叉验证
    cv_scores = cross_val_score(lr, X, y_raw, cv=5, scoring="r2")
    print(f"[交叉验证] 5折平均R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # 特征系数
    coef_df = pd.DataFrame({
        "特征": feature_cols,
        "系数": lr.coef_
    }).sort_values("系数", key=abs, ascending=False)
    print(f"\n[特征系数]")
    for _, row in coef_df.iterrows():
        direction = "正向" if row["系数"] > 0 else "负向"
        print(f"  {row['特征']}: {row['系数']:+.4f} ({direction})")
    print(f"  截距: {lr.intercept_:.4f}")

    # 保存模型
    model_path = MODEL_DIR / "linear_regression_salary.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": lr, "encoders": encoders}, f)
    print(f"\n[保存] {model_path}")

    # 可视化：预测 vs 实际
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(y_test, y_pred, alpha=0.6, edgecolors="white", c="#4472C4", s=50)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
            "r--", linewidth=2, label=f"完美预测 (R2={r2:.3f})")
    ax.set_xlabel("实际平均薪资 (K)", fontsize=11)
    ax.set_ylabel("预测平均薪资 (K)", fontsize=11)
    ax.set_title("线性回归：预测 vs 实际薪资", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    scatter_path = MODEL_DIR / "lr_prediction_vs_actual.png"
    fig.savefig(scatter_path, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"[保存] 散点图: {scatter_path}")

    return lr, r2


# ============================================================
# 3. 随机森林：预测招聘强度（特征重要性）
# ============================================================
def model_random_forest(df):
    print("\n" + "=" * 55)
    print("  模型3：随机森林 —— 预测招聘强度")
    print("=" * 55)

    feature_cols = ["city", "com_type", "com_size"]

    # 按 (city, com_type, com_size) 聚合，计算岗位数量作为"招聘强度"
    # 处理空值：填为"未知"
    df_rf = df[feature_cols].copy()
    for col in feature_cols:
        df_rf[col] = df_rf[col].fillna("未知").replace("", "未知")
    df_rf["job_count"] = 1
    agg_df = df_rf.groupby(feature_cols).size().reset_index(name="job_count")
    print(f"[聚合] 生成 {len(agg_df)} 个 (城市,企业类型,融资阶段) 组合")
    print(f"[标签] 招聘强度范围: {agg_df['job_count'].min()} ~ {agg_df['job_count'].max()}, 均值: {agg_df['job_count'].mean():.1f}")

    # LabelEncoder
    encoders = {}
    X = agg_df[feature_cols].copy()
    for col in feature_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    y = agg_df["job_count"].values

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE
    )

    # 训练随机森林
    rf = RandomForestRegressor(
        n_estimators=150,
        max_depth=8,
        min_samples_split=3,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    # 评估
    y_pred = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"\n[评估] R2: {r2:.4f}")
    print(f"[评估] RMSE: {rmse:.2f}")

    cv_scores = cross_val_score(rf, X, y, cv=5, scoring="r2")
    print(f"[交叉验证] 5折平均R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # 特征重要性
    importance_df = pd.DataFrame({
        "特征": feature_cols,
        "重要性": rf.feature_importances_
    }).sort_values("重要性", ascending=False)
    print(f"\n[特征重要性排名]")
    for _, row in importance_df.iterrows():
        print(f"  {row['特征']}: {row['重要性']:.4f} ({row['重要性']:.2%})")

    # 保存模型（附带上归一化参数：训练数据的 job_count min/max）
    y_min = float(y.min())
    y_max = float(y.max())
    model_path = MODEL_DIR / "random_forest_intensity.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": rf, "encoders": encoders, "y_min": y_min, "y_max": y_max}, f)
    print(f"\n[保存] {model_path} (job_count范围: {y_min}~{y_max})")

    # 可视化：特征重要性柱状图
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = ["#4472C4", "#ED7D31", "#A5A5A5"]
    bars = ax.barh(
        importance_df["特征"].tolist()[::-1],
        importance_df["重要性"].tolist()[::-1],
        color=colors[:len(importance_df)][::-1],
        height=0.45,
    )
    for bar, val in zip(bars, importance_df["重要性"].tolist()[::-1]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f} ({val:.1%})", va="center", fontsize=11, fontweight="bold")
    ax.set_xlim(0, importance_df["重要性"].max() * 1.25)
    ax.set_xlabel("特征重要性", fontsize=11)
    ax.set_title("随机森林：招聘强度特征重要性", fontsize=14, fontweight="bold")
    imp_path = MODEL_DIR / "rf_feature_importance.png"
    fig.savefig(imp_path, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"[保存] 特征重要性图: {imp_path}")

    # 各城市招聘强度均值（业务解读）
    print(f"\n[业务洞察] 各维度招聘强度均值:")
    for col in feature_cols:
        strength = agg_df.groupby(col)["job_count"].mean().sort_values(ascending=False)
        print(f"  [{col}]")
        for k, v in strength.items():
            print(f"    {k}: {v:.1f} 条/组")

    return rf, r2, importance_df


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 55)
    print("  Recruitment Role Data Analytics - 机器学习预测模型")
    print("=" * 55)

    df = load_data()

    # 模型1：决策树
    dt, dt_acc = model_decision_tree(df)

    # 模型2：线性回归
    lr, lr_r2 = model_linear_regression(df)

    # 模型3：随机森林
    rf, rf_r2, rf_importance = model_random_forest(df)

    # 汇总
    print("\n" + "=" * 55)
    print("  模型训练完成汇总")
    print("=" * 55)
    print(f"  决策树（城市分类）准确率: {dt_acc:.2%}")
    print(f"  线性回归（薪资预测）R2:   {lr_r2:.4f}")
    print(f"  随机森林（招聘强度）R2:    {rf_r2:.4f}")
    print(f"\n  模型文件:")
    for f in sorted(MODEL_DIR.glob("*.pkl")):
        size_kb = f.stat().st_size / 1024
        print(f"    {f.name}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
