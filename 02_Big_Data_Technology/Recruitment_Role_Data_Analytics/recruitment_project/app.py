# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics - 数据可视化Web平台
Flask + ECharts + MySQL
"""

import sys
import json
import pickle
from pathlib import Path

import pandas as pd

import requests
from flask import Flask, render_template, request, jsonify

# 将项目根目录加入 sys.path 以便导入共享模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL
from utils.database import get_dataframe
from utils import extract_benefits_keywords

# ============================================================
# 配置
# ============================================================
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__)
# 关闭 Flask 默认的 JSON 排序以获得更好性能
app.config["JSON_SORT_KEYS"] = False


# ============================================================
# 首页路由
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# API: 首页统计卡片
# ============================================================
@app.route("/api/stats")
def api_stats():
    df = get_dataframe()
    avg_sal = round((df["salary_lower"] + df["salary_high"]).mean() / 2, 1)
    max_sal = int(df["salary_high"].max())
    top_city = df["city"].value_counts().index[0]
    city_count = int(df["city"].nunique())
    return jsonify({
        "total_jobs": int(len(df)),
        "avg_salary": avg_sal,
        "max_salary": max_sal,
        "top_city": top_city,
        "city_count": city_count,
    })


# ============================================================
# API: 城市岗位分布
# ============================================================
@app.route("/api/city_distribution")
def api_city_distribution():
    df = get_dataframe()
    city_counts = df["city"].value_counts()
    return jsonify({
        "labels": city_counts.index.tolist(),
        "values": city_counts.values.tolist(),
    })


# ============================================================
# API: 学历要求分布
# ============================================================
@app.route("/api/education_distribution")
def api_education_distribution():
    df = get_dataframe()
    # 仅统计非空真实数据
    df_real = df[df["education"].notna() & (df["education"] != "")]
    edu_counts = df_real["education"].value_counts()
    edu_order = ["博士", "硕士", "本科", "大专"]
    ordered = {k: int(edu_counts.get(k, 0)) for k in edu_order}
    for k, v in edu_counts.items():
        if k not in ordered:
            ordered[k] = int(v)
    # 移除值为0的项
    ordered = {k: v for k, v in ordered.items() if v > 0}
    if not ordered:
        return jsonify({"labels": ["数据暂缺"], "values": [1], "note": "education字段均未采集到真实数据"})
    return jsonify({
        "labels": list(ordered.keys()),
        "values": list(ordered.values()),
        "coverage": f"{len(df_real)}/{len(df)}",
    })


# ============================================================
# API: 企业类型占比
# ============================================================
@app.route("/api/com_type_distribution")
def api_com_type_distribution():
    df = get_dataframe()
    # 仅统计非空真实数据（杜绝假数据混入）
    df_real = df[df["com_type"].notna() & (df["com_type"] != "")]
    type_counts = df_real["com_type"].value_counts()
    if len(type_counts) == 0:
        return jsonify({"labels": ["数据暂缺"], "values": [1], "note": "com_type字段均未能从51job解析"})
    return jsonify({
        "labels": type_counts.index.tolist(),
        "values": type_counts.values.tolist(),
        "coverage": f"{len(df_real)}/{len(df)}",
    })


# ============================================================
# API: 公司岗位排名TOP15
# ============================================================
@app.route("/api/company_top15")
def api_company_top15():
    df = get_dataframe()
    com_counts = df["com_name"].value_counts().head(15)
    return jsonify({
        "labels": com_counts.index.tolist(),
        "values": com_counts.values.tolist(),
    })


# ============================================================
# API: 工作经验与薪资关系
# ============================================================
@app.route("/api/workyear_salary")
def api_workyear_salary():
    df = get_dataframe()
    # 仅统计非空真实数据
    df_real = df[df["work_year"].notna() & (df["work_year"] != "")]
    if len(df_real) == 0:
        return jsonify({"error": "work_year字段均未采集到真实数据", "data": []})
    exp_order = ["应届", "1-3年", "3-5年", "5-10年", "10年以上"]
    df_real["avg_salary"] = (df_real["salary_lower"] + df_real["salary_high"]) / 2

    result = []
    for exp in exp_order:
        subset = df_real[df_real["work_year"] == exp]
        if len(subset) > 0:
            result.append({
                "work_year": exp,
                "avg_low": round(subset["salary_lower"].mean(), 1),
                "avg_high": round(subset["salary_high"].mean(), 1),
                "avg_salary": round(subset["avg_salary"].mean(), 1),
                "count": int(len(subset)),
            })
    # 也加入不在预设顺序中的经验值
    for exp in df_real["work_year"].unique():
        if exp not in exp_order:
            subset = df_real[df_real["work_year"] == exp]
            result.append({
                "work_year": exp,
                "avg_low": round(subset["salary_lower"].mean(), 1),
                "avg_high": round(subset["salary_high"].mean(), 1),
                "avg_salary": round(subset["avg_salary"].mean(), 1),
                "count": int(len(subset)),
            })

    return jsonify({"data": result, "coverage": f"{len(df_real)}/{len(df)}"})


# ============================================================
# API: 薪资区间分布
# ============================================================
@app.route("/api/salary_distribution")
def api_salary_distribution():
    df = get_dataframe()
    df["avg_salary"] = (df["salary_lower"] + df["salary_high"]) / 2

    bin_labels = ["0-10K", "10-20K", "20-30K", "30-40K", "40-50K", "50-60K", "60-70K"]
    bins = [0, 10, 20, 30, 40, 50, 60, 70]

    df["salary_bin"] = pd.cut(df["avg_salary"], bins=bins, labels=bin_labels, right=False)
    bin_counts = df["salary_bin"].value_counts().sort_index()

    return jsonify({
        "labels": bin_counts.index.tolist(),
        "values": bin_counts.values.tolist(),
    })


# ============================================================
# API: 融资阶段分布
# ============================================================
@app.route("/api/com_size_distribution")
def api_com_size_distribution():
    """企业规模分布（替代原融资阶段分布，基于真实com_size数据）"""
    df = get_dataframe()
    df_real = df[df["com_size"].notna() & (df["com_size"] != "")]
    size_counts = df_real["com_size"].value_counts()
    if len(size_counts) == 0:
        return jsonify({"labels": ["数据暂缺"], "values": [1], "note": "com_size字段均未采集到真实数据"})
    return jsonify({
        "labels": size_counts.index.tolist(),
        "values": size_counts.values.tolist(),
        "coverage": f"{len(df_real)}/{len(df)}",
    })


# ============================================================
# API: 岗位福利词频（用于词云）
# ============================================================
@app.route("/api/benefits_words")
def api_benefits_words():
    df = get_dataframe()
    benefits_text = " ".join(df["job_benefits"].dropna().astype(str).tolist())
    top_words = extract_benefits_keywords(benefits_text, top_n=120)
    return jsonify([
        {"name": w, "value": c} for w, c in top_words
    ])


# ============================================================
# API: 模型信息
# ============================================================
@app.route("/api/models_info")
def api_models_info():
    import numpy as np
    from sklearn.metrics import accuracy_score, r2_score
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import LabelEncoder
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor

    df = get_dataframe()
    result = {
        "decision_tree": {
            "name": "决策树 · 城市分类",
            "metric_name": "准确率",
            "metric_value": "--",
            "features": ["com_type", "com_size", "work_year", "education"],
            "label": "city",
        },
        "linear_regression": {
            "name": "线性回归 · 薪资预测",
            "metric_name": "R2",
            "metric_value": "--",
            "features": ["city", "work_year", "education", "com_type", "com_size"],
            "label": "平均薪资",
        },
        "random_forest": {
            "name": "随机森林 · 招聘强度",
            "metric_name": "R2",
            "metric_value": "--",
            "features": ["city", "com_type", "com_size"],
            "label": "招聘强度",
            "feature_importance": [
                {"feature": "企业类型", "importance": 0},
                {"feature": "企业规模", "importance": 0},
                {"feature": "城市", "importance": 0},
            ],
        },
        "random_forest_salary": {
            "name": "随机森林 · 薪资预测",
            "metric_name": "R2",
            "metric_value": "--",
            "features": ["city", "work_year", "education", "com_type", "com_size"],
            "label": "平均薪资",
            "feature_importance": [
                {"feature": "工作经验", "importance": 0},
                {"feature": "企业规模", "importance": 0},
                {"feature": "城市", "importance": 0},
                {"feature": "企业类型", "importance": 0},
                {"feature": "学历", "importance": 0},
            ],
        },
    }

    try:
        # 决策树准确率
        feature_cols_dt = ["com_type", "com_size", "work_year", "education"]
        X_raw = df[feature_cols_dt].copy()
        y_raw = df["city"].copy()
        valid_mask = y_raw.notna()
        X_raw = X_raw[valid_mask]
        y_raw = y_raw[valid_mask]
        for col in feature_cols_dt:
            X_raw[col] = X_raw[col].fillna("未知").replace("", "未知")
        encoders = {}
        X = X_raw.copy()
        for col in feature_cols_dt:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        y_le = LabelEncoder()
        y = y_le.fit_transform(y_raw)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        dt = DecisionTreeClassifier(max_depth=6, min_samples_split=5, min_samples_leaf=3, random_state=42)
        dt.fit(X_train, y_train)
        y_pred = dt.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        result["decision_tree"]["metric_value"] = f"{acc:.2%}"
        result["decision_tree"]["feature_importance"] = [
            {"feature": f, "importance": round(float(v), 4)} for f, v in zip(feature_cols_dt, dt.feature_importances_)
        ]
    except Exception as e:
        result["decision_tree"]["metric_value"] = "计算失败"

    try:
        # 线性回归 R2
        feature_cols_lr = ["city", "work_year", "education", "com_type", "com_size"]
        X_raw = df[feature_cols_lr].copy()
        y_raw = ((df["salary_lower"] + df["salary_high"]) / 2).copy()
        valid_mask = y_raw.notna()
        X_raw = X_raw[valid_mask]
        y_raw = y_raw[valid_mask]
        for col in feature_cols_lr:
            X_raw[col] = X_raw[col].fillna("未知").replace("", "未知")
        encoders = {}
        X = X_raw.copy()
        for col in feature_cols_lr:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        X_train, X_test, y_train, y_test = train_test_split(X, y_raw, test_size=0.25, random_state=42)
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        y_pred = lr.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        result["linear_regression"]["metric_value"] = f"{r2:.4f}"
    except Exception as e:
        result["linear_regression"]["metric_value"] = "计算失败"

    try:
        # 随机森林 R2
        feature_cols_rf = ["city", "com_type", "com_size"]
        df_rf = df[feature_cols_rf].copy()
        for col in feature_cols_rf:
            df_rf[col] = df_rf[col].fillna("未知").replace("", "未知")
        df_rf["job_count"] = 1
        agg_df = df_rf.groupby(feature_cols_rf).size().reset_index(name="job_count")
        encoders = {}
        X = agg_df[feature_cols_rf].copy()
        for col in feature_cols_rf:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        y = agg_df["job_count"].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        rf = RandomForestRegressor(n_estimators=150, max_depth=8, min_samples_split=3, min_samples_leaf=2, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        result["random_forest"]["metric_value"] = f"{r2:.4f}"
        result["random_forest"]["feature_importance"] = [
            {"feature": f, "importance": round(float(v), 4)} for f, v in zip(feature_cols_rf, rf.feature_importances_)
        ]
    except Exception as e:
        result["random_forest"]["metric_value"] = "计算失败"

    try:
        # 随机森林薪资 R2
        from sklearn.ensemble import RandomForestRegressor
        feature_cols_rfs = ["city", "work_year", "education", "com_type", "com_size"]
        X_raw = df[feature_cols_rfs].copy()
        y_raw = ((df["salary_lower"] + df["salary_high"]) / 2).copy()
        valid_mask = y_raw.notna()
        X_raw = X_raw[valid_mask]
        y_raw = y_raw[valid_mask]
        for col in feature_cols_rfs:
            X_raw[col] = X_raw[col].fillna("未知").replace("", "未知")
        encoders = {}
        X = X_raw.copy()
        for col in feature_cols_rfs:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        X_train, X_test, y_train, y_test = train_test_split(X, y_raw, test_size=0.25, random_state=42)
        rfs = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, min_samples_leaf=2, random_state=42, n_jobs=-1)
        rfs.fit(X_train, y_train)
        y_pred = rfs.predict(X_test)
        r2_rfs = r2_score(y_test, y_pred)
        result["random_forest_salary"]["metric_value"] = f"{r2_rfs:.4f}"
        result["random_forest_salary"]["feature_importance"] = [
            {"feature": f, "importance": round(float(v), 4)} for f, v in zip(feature_cols_rfs, rfs.feature_importances_)
        ]
    except Exception as e:
        result["random_forest_salary"]["metric_value"] = "计算失败"

    return jsonify(result)


# ============================================================
# API: 预测接口
# ============================================================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(force=True)
    city = data.get("city", "北京")
    education = data.get("education", "本科")
    work_year = data.get("work_year", "1-3年")
    com_type = data.get("com_type", "互联网")
    com_size = data.get("com_size", "100-499人")

    results = {}

    # --- 决策树：预测城市 ---
    try:
        dt_path = MODEL_DIR / "decision_tree_city.pkl"
        with open(dt_path, "rb") as f:
            dt_data = pickle.load(f)
        dt_model = dt_data["model"]
        dt_encoders = dt_data["encoders"]
        dt_label_enc = dt_data["label_encoder"]

        dt_input = pd.DataFrame([{
            "com_type": com_type,
            "com_size": com_size,
            "work_year": work_year,
            "education": education,
        }])
        for col in ["com_type", "com_size", "work_year", "education"]:
            le = dt_encoders[col]
            val = dt_input[col].iloc[0]
            if val in le.classes_:
                dt_input[col] = le.transform([val])[0]
            else:
                dt_input[col] = 0

        pred_city_idx = dt_model.predict(dt_input)[0]
        pred_city = dt_label_enc.inverse_transform([pred_city_idx])[0]
        probs = dt_model.predict_proba(dt_input)[0]
        prob_dict = {}
        for i, cls in enumerate(dt_label_enc.classes_):
            prob_dict[cls] = round(float(probs[i]) * 100, 2)
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)

        results["decision_tree"] = {
            "predicted_city": pred_city,
            "probabilities": dict(sorted_probs),
            "top3": [{"city": c, "prob": p} for c, p in sorted_probs[:3]],
        }
    except Exception as e:
        results["decision_tree"] = {"error": str(e)}

    # --- 线性回归：预测薪资 ---
    try:
        lr_path = MODEL_DIR / "linear_regression_salary.pkl"
        with open(lr_path, "rb") as f:
            lr_data = pickle.load(f)
        lr_model = lr_data["model"]
        lr_encoders = lr_data["encoders"]

        lr_input = pd.DataFrame([{
            "city": city,
            "work_year": work_year,
            "education": education,
            "com_type": com_type,
            "com_size": com_size,
        }])
        for col in ["city", "work_year", "education", "com_type", "com_size"]:
            le = lr_encoders[col]
            val = lr_input[col].iloc[0]
            if val in le.classes_:
                lr_input[col] = le.transform([val])[0]
            else:
                lr_input[col] = 0

        pred_salary = float(lr_model.predict(lr_input)[0])
        results["linear_regression"] = {
            "predicted_salary_k": round(pred_salary, 1),
            "predicted_salary_range": f"{max(0, int(pred_salary - 5))}K-{int(pred_salary + 5)}K",
        }
    except Exception as e:
        results["linear_regression"] = {"error": str(e)}

    # --- 随机森林：预测薪资（第二种算法） ---
    try:
        rf_sal_path = MODEL_DIR / "random_forest_salary.pkl"
        with open(rf_sal_path, "rb") as f:
            rf_sal_data = pickle.load(f)
        rf_sal_model = rf_sal_data["model"]
        rf_sal_encoders = rf_sal_data["encoders"]

        rf_sal_input = pd.DataFrame([{
            "city": city,
            "work_year": work_year,
            "education": education,
            "com_type": com_type,
            "com_size": com_size,
        }])
        for col in ["city", "work_year", "education", "com_type", "com_size"]:
            le = rf_sal_encoders[col]
            val = rf_sal_input[col].iloc[0]
            if val in le.classes_:
                rf_sal_input[col] = le.transform([val])[0]
            else:
                rf_sal_input[col] = 0

        pred_rf_salary = float(rf_sal_model.predict(rf_sal_input)[0])
        results["random_forest_salary"] = {
            "predicted_salary_k": round(pred_rf_salary, 1),
            "predicted_salary_range": f"{max(0, int(pred_rf_salary - 5))}K-{int(pred_rf_salary + 5)}K",
        }
    except Exception as e:
        results["random_forest_salary"] = {"error": str(e)}

    # --- 随机森林：预测招聘强度 ---
    try:
        rf_path = MODEL_DIR / "random_forest_intensity.pkl"
        with open(rf_path, "rb") as f:
            rf_data = pickle.load(f)
        rf_model = rf_data["model"]
        rf_encoders = rf_data["encoders"]
        # 兼容旧模型（无 y_min/y_max），默认使用训练数据实际范围
        y_min = rf_data.get("y_min", 1)
        y_max = rf_data.get("y_max", 54)

        rf_input = pd.DataFrame([{
            "city": city,
            "com_type": com_type,
            "com_size": com_size,
        }])
        for col in ["city", "com_type", "com_size"]:
            le = rf_encoders[col]
            val = rf_input[col].iloc[0]
            if val in le.classes_:
                rf_input[col] = le.transform([val])[0]
            else:
                rf_input[col] = 0

        pred_intensity = float(rf_model.predict(rf_input)[0])

        # Min-Max 归一化到 0-100：score = (pred - min) / (max - min) * 100
        # 用百分位数（P95）作为上限参考，避免极端值拉低大部分评分
        p95 = y_min + (y_max - y_min) * 0.95
        if pred_intensity <= y_min:
            intensity_score = 0.0
        elif pred_intensity >= p95:
            intensity_score = 100.0
        else:
            intensity_score = round((pred_intensity - y_min) / (p95 - y_min) * 100, 1)

        # 确定等级：0-30 低，30-65 中，65-100 高
        if intensity_score >= 65:
            level = "高"
        elif intensity_score >= 30:
            level = "中"
        else:
            level = "低"

        results["random_forest"] = {
            "predicted_intensity": round(pred_intensity, 2),
            "intensity_score": intensity_score,
            "intensity_level": level,
        }
    except Exception as e:
        results["random_forest"] = {"error": str(e)}

    return jsonify(results)


# ============================================================
# API: 薪资算法对比（线性回归 vs 随机森林）
# ============================================================
@app.route("/api/salary/compare", methods=["POST"])
def api_salary_compare():
    data = request.get_json(force=True)
    city = data.get("city", "北京")
    education = data.get("education", "本科")
    work_year = data.get("work_year", "1-3年")
    com_type = data.get("com_type", "互联网")
    com_size = data.get("com_size", "100-499人")
    result = {}
    # Linear Regression
    try:
        lr_path = MODEL_DIR / "linear_regression_salary.pkl"
        with open(lr_path, "rb") as f:
            lr_data = pickle.load(f)
        lr_model = lr_data["model"]
        lr_encoders = lr_data["encoders"]
        lr_metrics = lr_data.get("metrics", {})
        lr_input = pd.DataFrame([{"city": city, "work_year": work_year, "education": education, "com_type": com_type, "com_size": com_size}])
        for col in ["city", "work_year", "education", "com_type", "com_size"]:
            le = lr_encoders[col]; val = lr_input[col].iloc[0]
            lr_input[col] = le.transform([val])[0] if val in le.classes_ else 0
        pred_lr = float(lr_model.predict(lr_input)[0])
        result["linear_regression"] = {"predicted_salary_k": round(pred_lr, 1), "range": f"{max(0, int(pred_lr-5))}K-{int(pred_lr+5)}K", "metrics": {"r2": round(lr_metrics.get('r2',0),4), "rmse": round(lr_metrics.get('rmse',0),2), "mae": round(lr_metrics.get('mae',0),2)}}
    except Exception as e:
        result["linear_regression"] = {"error": str(e)}
    # Random Forest
    try:
        rf_path = MODEL_DIR / "random_forest_salary.pkl"
        with open(rf_path, "rb") as f:
            rf_data = pickle.load(f)
        rf_model = rf_data["model"]
        rf_encoders = rf_data["encoders"]
        rf_metrics = rf_data.get("metrics", {})
        rf_features = rf_data.get("features", [])
        rf_input = pd.DataFrame([{"city": city, "work_year": work_year, "education": education, "com_type": com_type, "com_size": com_size}])
        for col in ["city", "work_year", "education", "com_type", "com_size"]:
            le = rf_encoders[col]; val = rf_input[col].iloc[0]
            rf_input[col] = le.transform([val])[0] if val in le.classes_ else 0
        pred_rf = float(rf_model.predict(rf_input)[0])
        fi = []
        if hasattr(rf_model, "feature_importances_"):
            for f_name, imp in zip(rf_features, rf_model.feature_importances_):
                fi.append({"feature": f_name, "importance": round(float(imp), 4)})
        result["random_forest"] = {"predicted_salary_k": round(pred_rf, 1), "range": f"{max(0, int(pred_rf-5))}K-{int(pred_rf+5)}K", "metrics": {"r2": round(rf_metrics.get('r2',0),4), "rmse": round(rf_metrics.get('rmse',0),2), "mae": round(rf_metrics.get('mae',0),2)}, "feature_importance": fi}
    except Exception as e:
        result["random_forest"] = {"error": str(e)}
    return jsonify(result)


# ============================================================
# API: 获取表单选项
# ============================================================
@app.route("/api/form_options")
def api_form_options():
    df = get_dataframe()
    # 仅返回非空真实选项
    education_opts = sorted([x for x in df["education"].dropna().unique() if x != ""])
    work_year_opts = sorted([x for x in df["work_year"].dropna().unique() if x != ""])
    com_type_opts = sorted([x for x in df["com_type"].dropna().unique() if x != ""])
    com_size_opts = sorted([x for x in df["com_size"].dropna().unique() if x != ""])
    return jsonify({
        "city": sorted(df["city"].dropna().unique().tolist()),
        "education": education_opts if education_opts else ["博士", "硕士", "本科", "大专"],
        "work_year": work_year_opts if work_year_opts else ["应届", "1-3年", "3-5年", "5-10年", "10年以上"],
        "com_type": com_type_opts if com_type_opts else [],
        "com_size": com_size_opts if com_size_opts else [],
    })


# ============================================================
# DeepSeek AI 智能问答配置（从共享 config 模块导入）
# ============================================================

# 系统提示词：让 AI 了解平台数据背景
SYSTEM_PROMPT = """你是 Recruitment Role Data Analytics 平台的 AI 助手。你拥有以下知识：

平台数据概况：
- 数据来源：51job 真实爬取，存储于 recruitment_db.t_recruitment_info
- 覆盖城市：北京、上海、深圳、广州、杭州（5大热门城市）
- 岗位类型：数据分析、数据开发、大数据、数据挖掘、数据工程师、BI工程师、商业分析、统计分析师、数据产品经理、ETL开发
- 数据维度：岗位名称、薪资范围、公司名称、企业类型、企业规模、工作经验、学历要求、福利标签、城市、地区
- 注意：学历和工作经验字段来自51job标题/标签的正则提取，覆盖率可能有限，部分数据可能缺失

平台功能：
1. 数据看板：城市岗位分布、学历分布、企业类型占比、公司排名TOP15、工作经验与薪资关系、薪资区间分布、企业规模分布、福利词云
2. AI预测：决策树城市分类、线性回归薪资预测、随机森林薪资预测（双算法对比）、随机森林招聘强度预测

你的职责：
1. 为用户解答数据相关岗位的就业市场问题
2. 解读平台上的图表和数据趋势
3. 提供职业发展建议、行业洞察
4. 分析不同城市/学历/经验对薪资的影响
5. 以专业、友好的口吻回答用户问题
6. 回答尽量简洁明了，使用中文
7. 如果数据维度数据缺失，诚实地告知用户，切勿编造数据
"""

# 对话历史缓存（服务内存级别，每次重启清空）
chat_sessions = {}


# ============================================================
# API: AI 智能问答
# ============================================================
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "消息不能为空"}), 400

    # 获取对话历史
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = chat_sessions[session_id]

    # 附加当前数据摘要（每次请求动态刷新）
    try:
        df = get_dataframe()
        edu_real = df[df["education"].notna() & (df["education"] != "")]
        wy_real = df[df["work_year"].notna() & (df["work_year"] != "")]
        ct_real = df[df["com_type"].notna() & (df["com_type"] != "")]
        cs_real = df[df["com_size"].notna() & (df["com_size"] != "")]
        data_summary = f"""
当前数据库真实数据摘要（共{len(df)}条）：
- 城市分布：{dict(df['city'].value_counts().to_dict())}
- 平均薪资：{(df['salary_lower'] + df['salary_high']).mean() / 2:.1f}K/月
- 学历分布（覆盖率{len(edu_real)}/{len(df)}）：{dict(edu_real['education'].value_counts().to_dict()) if len(edu_real) > 0 else '数据暂缺'}
- 经验分布（覆盖率{len(wy_real)}/{len(df)}）：{dict(wy_real['work_year'].value_counts().to_dict()) if len(wy_real) > 0 else '数据暂缺'}
- 企业类型TOP3（覆盖率{len(ct_real)}/{len(df)}）：{dict(ct_real['com_type'].value_counts().head(3).to_dict()) if len(ct_real) > 0 else '数据暂缺'}
- 企业规模TOP3（覆盖率{len(cs_real)}/{len(df)}）：{dict(cs_real['com_size'].value_counts().head(3).to_dict()) if len(cs_real) > 0 else '数据暂缺'}
"""
        # 将数据摘要作为系统消息追加
        context_msg = {"role": "system", "content": f"【实时数据】{data_summary}"}
        messages = [history[0], context_msg] + history[1:] + [{"role": "user", "content": user_message}]
    except Exception:
        messages = history + [{"role": "user", "content": user_message}]

    # 调用 DeepSeek API
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500,
            "stream": False,
        }

        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        result = resp.json()

        ai_reply = result["choices"][0]["message"]["content"]

        # 更新对话历史
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_reply})

        # 限制历史长度（最近 20 轮）
        if len(history) > 21:
            chat_sessions[session_id] = [history[0]] + history[-20:]

        return jsonify({
            "reply": ai_reply,
            "session_id": session_id,
            "history_count": (len(history) - 1) // 2,  # 对话轮数
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "DeepSeek API 请求超时，请稍后重试"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API 请求失败: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


# ============================================================
# API: 清空对话历史
# ============================================================
@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id", "default")
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({"status": "ok", "message": "对话历史已清空"})


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  Recruitment Role Data Analytics Web平台")
    print(f"  地址: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(host="127.0.0.1", port=5000, debug=False)
