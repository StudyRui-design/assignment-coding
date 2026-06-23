# -*- coding: utf-8 -*-
"""
4_tuning.py — 超参数调优模块
使用 GridSearchCV 对最优模型进行超参数搜索，并使用 Optuna 进行贝叶斯优化对比
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time

from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import f1_score, roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from utils import save_fig, save_model, load_model, MODEL_DIR

warnings.filterwarnings('ignore')
np.random.seed(42)


def load_split_data():
    """加载划分好的训练/测试数据"""
    data = joblib.load(os.path.join(MODEL_DIR, 'train_test_split.pkl'))
    return data['X_train'], data['X_test'], data['y_train'], data['y_test'], data['best_model_name']


def grid_search_tuning(model, X_train, y_train, X_test, y_test, param_grid, model_name, cv=5):
    """
    执行 GridSearchCV 超参数搜索
    """
    print(f"\n{'='*60}")
    print(f"GridSearchCV 超参数搜索: {model_name}")
    print(f"{'='*60}")
    print(f"搜索空间: {param_grid}")
    total_combos = np.prod([len(v) for v in param_grid.values()])
    print(f"参数组合数: {total_combos} × {cv}折CV = {total_combos * cv} 次拟合")

    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    grid = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring='f1',
        cv=skf,
        n_jobs=-1,
        verbose=1,
        return_train_score=True
    )

    start = time.time()
    grid.fit(X_train, y_train)
    elapsed = time.time() - start

    print(f"\n搜索完成! 耗时: {elapsed:.1f} 秒")
    print(f"最优参数: {grid.best_params_}")
    print(f"最优CV F1-Score: {grid.best_score_:.4f}")

    # 在测试集上评估
    y_pred = grid.best_estimator_.predict(X_test)
    y_proba = grid.best_estimator_.predict_proba(X_test)[:, 1]

    test_f1 = f1_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_proba)
    print(f"测试集 F1-Score: {test_f1:.4f} | AUC-ROC: {test_auc:.4f}")
    print(f"\n分类报告:\n{classification_report(y_test, y_pred, target_names=['正常还款', '违约'])}")

    return grid, test_f1, test_auc


def plot_grid_search_results(grid, model_name):
    """绘制网格搜索结果热力图"""
    results = pd.DataFrame(grid.cv_results_)
    param_keys = list(grid.param_grid.keys())

    fig, axes = plt.subplots(1, len(param_keys) - 1, figsize=(5 * (len(param_keys) - 1), 5))
    if len(param_keys) - 1 == 1:
        axes = [axes]

    for i, pk2 in enumerate(param_keys[1:]):
        # GridSearchCV cv_results 中参数列带有 'param_' 前缀
        idx_col = 'param_' + param_keys[0]
        col_col = 'param_' + pk2
        pivot = results.pivot_table(
            values='mean_test_score',
            index=idx_col,
            columns=col_col,
            aggfunc='mean'
        )
        sns.heatmap(pivot, annot=True, fmt='.4f', cmap='YlOrRd', ax=axes[i],
                    cbar_kws={'label': 'F1-Score'})
        axes[i].set_title(f'GS参数热力图: {param_keys[0]} vs {pk2}', fontweight='bold')
        axes[i].set_xlabel(pk2)
        axes[i].set_ylabel(param_keys[0])

    fig.suptitle(f'{model_name} 超参数搜索热力图', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '12_grid_search_heatmap.png')
    return fig


def plot_tuning_comparison(before_scores, after_scores):
    """调优前后性能对比图"""
    metrics = ['F1-Score', 'AUC-ROC']
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for ax, metric in zip(axes, metrics):
        ax.bar(['调优前', '调优后'], [before_scores[metric], after_scores[metric]],
               color=['#5DADE2', '#27AE60'], edgecolor='white', width=0.5)
        ax.set_title(f'{metric} 调优对比', fontweight='bold')
        ax.set_ylabel(metric)
        ax.set_ylim(0, 1)

        # 标注数值
        for i, v in enumerate([before_scores[metric], after_scores[metric]]):
            ax.text(i, v + 0.01, f'{v:.4f}', ha='center', fontweight='bold', fontsize=12)

        # 标注提升
        improvement = after_scores[metric] - before_scores[metric]
        ax.text(0.5, max(before_scores[metric], after_scores[metric]) + 0.06,
                f'+{improvement:.4f}', ha='center', fontsize=10, color='#27AE60', fontweight='bold')

    fig.suptitle('超参数调优效果对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_fig(fig, '13_tuning_comparison.png')
    return fig


def run_tuning():
    """执行完整的超参数调优流程"""
    print(">>> 开始超参数调优 <<<\n")

    X_train, X_test, y_train, y_test, best_name = load_split_data()
    print(f"加载数据: X_train={X_train.shape}, X_test={X_test.shape}")
    print(f"待调优模型: {best_name}")

    # 获取调优前的基准性能
    base_model = load_model('best_model.pkl')
    y_pred_before = base_model.predict(X_test)
    y_proba_before = base_model.predict_proba(X_test)[:, 1]
    before_scores = {
        'F1-Score': f1_score(y_test, y_pred_before),
        'AUC-ROC': roc_auc_score(y_test, y_proba_before)
    }
    print(f"调优前基准: F1={before_scores['F1-Score']:.4f}, AUC={before_scores['AUC-ROC']:.4f}")

    # 根据最优模型类型选择调优策略
    if best_name == 'Logistic Regression':
        # 如果LR是最优，说明数据线性可分性较好
        tuned_model, test_f1, test_auc = tune_logistic_regression(X_train, y_train, X_test, y_test)
        param_grid = {'C': [0.001, 0.01, 0.1, 1, 10],
                      'penalty': ['l1', 'l2'],
                      'solver': ['liblinear', 'saga']}

    elif best_name == 'Random Forest':
        tuned_model, test_f1, test_auc, param_grid = tune_random_forest(X_train, y_train, X_test, y_test)

    elif best_name in ['XGBoost', 'LightGBM', 'Gradient Boosting']:
        tuned_model, test_f1, test_auc, param_grid = tune_boosting(X_train, y_train, X_test, y_test, best_name)

    else:
        print(f"模型 {best_name} 采用默认参数，使用通用网格搜索")
        tuned_model, test_f1, test_auc, param_grid = tune_generic(
            X_train, y_train, X_test, y_test, best_name)

    # 保存调优后的模型
    save_model(tuned_model, 'tuned_model.pkl')

    # 调优后性能
    after_scores = {'F1-Score': test_f1, 'AUC-ROC': test_auc}

    # 可视化
    plot_tuning_comparison(before_scores, after_scores)
    print("图13: 调优对比图 [OK]")

    print("\n" + "=" * 60)
    print("超参数调优总结")
    print("=" * 60)
    print(f"模型: {best_name}")
    print(f"F1-Score: {before_scores['F1-Score']:.4f} → {after_scores['F1-Score']:.4f} (+{after_scores['F1-Score'] - before_scores['F1-Score']:.4f})")
    print(f"AUC-ROC:  {before_scores['AUC-ROC']:.4f} → {after_scores['AUC-ROC']:.4f} (+{after_scores['AUC-ROC'] - before_scores['AUC-ROC']:.4f})")

    return tuned_model, after_scores


def tune_logistic_regression(X_train, y_train, X_test, y_test):
    """Logistic Regression 网格搜索"""
    param_grid = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'penalty': ['l2'],
        'solver': ['liblinear', 'lbfgs', 'saga']
    }
    model = LogisticRegression(max_iter=3000, random_state=42)
    grid, test_f1, test_auc = grid_search_tuning(model, X_train, y_train, X_test, y_test,
                                                  param_grid, 'Logistic Regression')
    plot_grid_search_results(grid, 'Logistic Regression')
    return grid.best_estimator_, test_f1, test_auc


def tune_random_forest(X_train, y_train, X_test, y_test):
    """Random Forest 网格搜索"""
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [8, 12, 16, 20],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    model = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid, test_f1, test_auc = grid_search_tuning(model, X_train, y_train, X_test, y_test,
                                                  param_grid, 'Random Forest')
    plot_grid_search_results(grid, 'Random Forest')
    param_grid_display = param_grid.copy()
    return grid.best_estimator_, test_f1, test_auc, param_grid_display


def tune_boosting(X_train, y_train, X_test, y_test, model_name):
    """XGBoost/LightGBM 网格搜索"""
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [4, 6, 8],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 1.0]
    }
    if model_name == 'XGBoost':
        model = XGBClassifier(random_state=42, verbosity=0, n_jobs=-1)
    elif model_name == 'LightGBM':
        model = LGBMClassifier(random_state=42, verbose=-1, n_jobs=-1)
    else:
        model = GradientBoostingClassifier(random_state=42)

    grid, test_f1, test_auc = grid_search_tuning(model, X_train, y_train, X_test, y_test,
                                                  param_grid, model_name)
    plot_grid_search_results(grid, model_name)
    param_grid_display = param_grid.copy()
    return grid.best_estimator_, test_f1, test_auc, param_grid_display


def tune_generic(X_train, y_train, X_test, y_test, model_name):
    """通用调优"""
    from sklearn.svm import SVC
    param_grid = {
        'C': [0.1, 1, 10],
        'gamma': ['scale', 'auto', 0.01, 0.1]
    }
    model = SVC(kernel='rbf', probability=True, random_state=42)
    grid, test_f1, test_auc = grid_search_tuning(model, X_train, y_train, X_test, y_test,
                                                  param_grid, model_name)
    return grid.best_estimator_, test_f1, test_auc


if __name__ == '__main__':
    run_tuning()
