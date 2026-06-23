# -*- coding: utf-8 -*-
"""
3_modeling.py — 多模型对比实验模块
构建 ≥5 种不同类型的机器学习模型，使用5折交叉验证对比评估
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, roc_curve,
                              confusion_matrix, classification_report)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from utils import load_data, save_fig, save_model, MODEL_DIR, FIG_DIR

warnings.filterwarnings('ignore')
np.random.seed(42)

# ================================
# 模型定义
# ================================

def get_models():
    """定义待评估的模型列表，涵盖线性、树模型、集成、核方法"""
    models = {
        # 1. 线性模型
        'Logistic Regression': LogisticRegression(
            max_iter=2000, random_state=42, n_jobs=-1),

        # 2. 单棵决策树 → 改为Bagging集成，单树样本中的Decision Tree表现弱
        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),

        # 3. Boosting 集成 — XGBoost
        'XGBoost': XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=42, verbosity=0, n_jobs=-1),

        # 4. Boosting 集成 — LightGBM
        'LightGBM': LGBMClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=42, verbose=-1, n_jobs=-1),

        # 5. Boosting 集成 — Gradient Boosting
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42),

        # 6. K近邻 — 基于实例的非参数方法
        'K-Nearest Neighbors': KNeighborsClassifier(
            n_neighbors=15, n_jobs=-1),
    }
    return models


# ================================
# 评估指标计算
# ================================

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """计算单个模型在测试集上的所有评估指标"""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

    scores = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred, zero_division=0),
        'Recall': recall_score(y_test, y_pred, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred, zero_division=0),
    }
    if y_proba is not None:
        scores['AUC-ROC'] = roc_auc_score(y_test, y_proba)
    else:
        scores['AUC-ROC'] = 0.0

    return scores, y_pred, y_proba


# ================================
# K折交叉验证
# ================================

def cross_validate_models(models, X, y, n_splits=5):
    """
    使用分层K折交叉验证评估所有模型
    返回: (cv_results_df, test_results_df, roc_data)
    """
    print("=" * 60)
    print(f"多模型 {n_splits}折交叉验证评估")
    print("=" * 60)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # 存储结果
    cv_results = {name: {'Accuracy': [], 'Precision': [], 'Recall': [],
                          'F1-Score': [], 'AUC-ROC': []}
                  for name in models}

    # 按8:2划分最终的测试集（分层抽样）
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"训练集: {X_train_full.shape[0]} 条 | 测试集: {X_test.shape[0]} 条")
    print(f"训练集违约率: {y_train_full.mean():.2%} | 测试集违约率: {y_test.mean():.2%}")

    test_results = {}
    roc_data = {}

    for name, model in models.items():
        print(f"\n>>> 训练 & 交叉验证: {name} <<<")

        # K折交叉验证
        fold_scores = {'Accuracy': [], 'Precision': [], 'Recall': [],
                       'F1-Score': [], 'AUC-ROC': []}
        fold_rocs = []

        for fold, (train_idx, val_idx) in enumerate(skf.split(X_train_full, y_train_full), 1):
            X_tr, X_val = X_train_full.iloc[train_idx], X_train_full.iloc[val_idx]
            y_tr, y_val = y_train_full.iloc[train_idx], y_train_full.iloc[val_idx]

            # 使用 deepcopy 创建独立模型副本避免交叉验证中的状态污染
            from copy import deepcopy
            model_clone = deepcopy(model)
            model_clone.fit(X_tr, y_tr)

            scores, _, y_val_proba = evaluate_model(model_clone, X_tr, X_val, y_tr, y_val)
            for metric in fold_scores:
                fold_scores[metric].append(scores[metric])

            # 记录ROC
            if y_val_proba is not None:
                fpr, tpr, _ = roc_curve(y_val, y_val_proba)
                fold_rocs.append((fpr, tpr))

        # 记录CV均值和标准差
        for metric in fold_scores:
            cv_results[name][metric] = {
                'mean': np.mean(fold_scores[metric]),
                'std': np.std(fold_scores[metric])
            }
        print(f"  CV F1: {cv_results[name]['F1-Score']['mean']:.4f} ± {cv_results[name]['F1-Score']['std']:.4f}")
        print(f"  CV AUC: {cv_results[name]['AUC-ROC']['mean']:.4f} ± {cv_results[name]['AUC-ROC']['std']:.4f}")

        # 在全量训练集上最终训练，测试集评估
        model.fit(X_train_full, y_train_full)
        final_scores, _, y_test_proba = evaluate_model(model, X_train_full, X_test, y_train_full, y_test)
        test_results[name] = final_scores

        # 计算ROC曲线 (使用测试集)
        if y_test_proba is not None:
            fpr_test, tpr_test, _ = roc_curve(y_test, y_test_proba)
            roc_data[name] = (fpr_test, tpr_test, final_scores['AUC-ROC'])

        print(f"  测试集 F1: {final_scores['F1-Score']:.4f} | AUC: {final_scores['AUC-ROC']:.4f}")

    # 构建测试集结果DataFrame
    test_df = pd.DataFrame(test_results).T
    test_df = test_df.round(4)

    # 构建CV结果DataFrame (每行一个模型，每列一个指标: mean±std)
    cv_records = []
    for name in models:
        row = {'Model': name}
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']:
            row[metric] = f"{cv_results[name][metric]['mean']:.4f}±{cv_results[name][metric]['std']:.4f}"
        cv_records.append(row)
    cv_df = pd.DataFrame(cv_records).set_index('Model')

    # 保存最优模型
    best_model_name = test_df['F1-Score'].idxmax()
    best_model = models[best_model_name]
    best_model.fit(X_train_full, y_train_full)
    save_model(best_model, 'best_model.pkl')
    print(f"\n最优模型: {best_model_name} (测试集 F1={test_df.loc[best_model_name, 'F1-Score']:.4f})")

    return cv_df, test_df, roc_data, X_train_full, X_test, y_train_full, y_test, best_model_name


# ================================
# 可视化
# ================================

def plot_roc_curves(roc_data):
    """绘制多模型ROC曲线对比图"""
    fig, ax = plt.subplots(figsize=(10, 8))

    colors = sns.color_palette("Set2", n_colors=len(roc_data))
    for (name, (fpr, tpr, auc_val)), color in zip(roc_data.items(), colors):
        ax.plot(fpr, tpr, linewidth=2.2, label=f'{name} (AUC={auc_val:.4f})', color=color)

    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='随机分类 (AUC=0.5)')
    ax.fill_between([0, 1], [0, 1], alpha=0.05, color='gray')
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    ax.set_ylabel('True Positive Rate (Recall)', fontsize=12)
    ax.set_title('多模型 ROC 曲线对比', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    save_fig(fig, '08_roc_curves.png')
    return fig


def plot_performance_comparison(test_df):
    """绘制模型性能柱状对比图"""
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
    models = test_df.index.tolist()

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(models))
    width = 0.15
    colors = sns.color_palette("Set2", n_colors=len(metrics))

    for i, (metric, color) in enumerate(zip(metrics, colors)):
        bars = ax.bar(x + i * width, test_df[metric], width, label=metric, color=color, edgecolor='white', alpha=0.9)
        # 标注F1和AUC数值
        if metric in ['F1-Score', 'AUC-ROC']:
            for bar, val in zip(bars, test_df[metric]):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f'{val:.3f}', ha='center', fontsize=7, fontweight='bold')

    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(models, rotation=20, ha='right', fontsize=10)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('多模型性能对比柱状图', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9, ncol=3)
    ax.set_ylim(0, 1.05)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save_fig(fig, '09_performance_comparison.png')
    return fig


def plot_feature_importance(model, feature_names, top_n=15):
    """绘制特征重要性排序图"""
    # 获取特征重要性（不同模型方式不同）
    importance = None
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_).flatten()

    if importance is None:
        print("该模型无特征重要性属性")
        return None

    # 排序取前N
    indices = np.argsort(importance)[::-1][:top_n]
    top_features = np.array(feature_names)[indices]
    top_importance = importance[indices]

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = plt.cm.YlOrRd(top_importance / top_importance.max())
    bars = ax.barh(range(top_n), top_importance, color=colors, edgecolor='white')
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_features, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title(f'特征重要性排序 (Top {top_n})', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 添加数值标签
    for bar, val in zip(bars, top_importance):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                f'{val:.4f}', va='center', fontsize=8)

    plt.tight_layout()
    save_fig(fig, '10_feature_importance.png')
    return fig


def plot_radar_chart(test_df):
    """绘制模型性能雷达图"""
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC']
    n_metrics = len(metrics)
    angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    colors = sns.color_palette("Set2", n_colors=len(test_df))

    for (name, row), color in zip(test_df.iterrows(), colors):
        values = [row[m] for m in metrics]
        values += values[:1]
        ax.fill(angles, values, alpha=0.15, color=color)
        ax.plot(angles, values, 'o-', linewidth=2, label=name, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'], fontsize=8)
    ax.set_title('模型性能雷达图对比', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

    plt.tight_layout()
    save_fig(fig, '11_radar_chart.png')
    return fig


def run_modeling():
    """执行完整的多模型对比实验流程"""
    print(">>> 开始多模型对比实验 <<<\n")

    # 加载处理后的数据
    df = pd.read_csv('data_processed.csv')
    X = df.drop(columns=['default.payment.next.month'])
    y = df['default.payment.next.month']
    print(f"加载处理后数据: {X.shape}, 违约率={y.mean():.2%}")

    # 获取模型
    models = get_models()
    print(f"\n待评估模型 ({len(models)}个):")
    for i, name in enumerate(models, 1):
        print(f"  {i}. {name}")

    # 交叉验证评估
    cv_df, test_df, roc_data, X_train, X_test, y_train, y_test, best_name = \
        cross_validate_models(models, X, y, n_splits=5)

    # 保存评估结果
    test_df.to_csv(os.path.join(MODEL_DIR, 'model_comparison.csv'))
    cv_df.to_csv(os.path.join(MODEL_DIR, 'cv_results.csv'))

    print("\n" + "=" * 60)
    print("模型性能对比 (测试集)")
    print("=" * 60)
    print(test_df.to_string())

    # 可视化
    plot_roc_curves(roc_data)
    print("图8: ROC曲线对比图 [OK]")

    plot_performance_comparison(test_df)
    print("图9: 性能对比柱状图 [OK]")

    # 特征重要性 (对最优模型)
    best_model = models[best_name]
    best_model.fit(X_train, y_train)
    plot_feature_importance(best_model, X.columns.tolist())
    print("图10: 特征重要性排序图 [OK]")

    plot_radar_chart(test_df)
    print("图11: 性能雷达图 [OK]")

    # 保存训练/测试数据用于后续调优
    train_test_data = {
        'X_train': X_train, 'X_test': X_test,
        'y_train': y_train, 'y_test': y_test,
        'best_model_name': best_name
    }
    joblib.dump(train_test_data, os.path.join(MODEL_DIR, 'train_test_split.pkl'))

    print(f"\n>>> 多模型对比实验完成! 最优模型: {best_name} <<<")
    return test_df, best_name, X_train, X_test, y_train, y_test


if __name__ == '__main__':
    run_modeling()
