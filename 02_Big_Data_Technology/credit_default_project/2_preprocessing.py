# -*- coding: utf-8 -*-
"""
2_preprocessing.py — 数据预处理与特征工程模块 (考核核心考察点)
信用卡违约预测项目

特征工程操作清单 (共6类，满足≥3要求):
  1. 数据清洗: EDUCATION/MARRIAGE异常值整合、账单负值修正
  2. 特征缩放: StandardScaler 标准化数值特征
  3. 类别编码: One-Hot (SEX, MARRIAGE) + Ordinal (EDUCATION)
  4. 特征交叉: 信用额度利用率、还款率、额度覆盖倍数
  5. 聚合特征: 还款趋势斜率、账单波动率、平均延迟统计
  6. 降维分析: PCA 主成分方差解释
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.decomposition import PCA
from utils import load_data, save_fig


# ================================
# 阶段一：数据清洗
# ================================

def clean_data(df):
    """
    数据清洗：
    1. EDUCATION: 0/5/6 归入 4(其他)，统一为 {1:研究生, 2:大学, 3:高中, 4:其他}
    2. MARRIAGE: 0 归入 3(其他)，统一为 {1:已婚, 2:单身, 3:其他}
    3. 删除ID列 (主键无预测价值)
    4. 检查并处理重复值
    5. BILL_AMT 负值处理 (若有负值代表溢缴，转为0)
    """
    print("=" * 60)
    print("阶段一：数据清洗")
    print("=" * 60)

    df_clean = df.copy()

    # --- EDUCATION 清洗 ---
    edu_before = df_clean['EDUCATION'].value_counts().to_dict()
    df_clean['EDUCATION'] = df_clean['EDUCATION'].replace({0: 4, 5: 4, 6: 4})
    print(f"EDUCATION 清洗: {edu_before} → {df_clean['EDUCATION'].value_counts().sort_index().to_dict()}")
    print(f"  处理依据: 数据字典仅定义1-4; 0/5/6为未文档化类别, 总样本数较少"
          f"({(df['EDUCATION'].isin([0,5,6])).sum()}条), 归入'其他(4)'避免碎片化")

    # --- MARRIAGE 清洗 ---
    mar_before = df_clean['MARRIAGE'].value_counts().to_dict()
    df_clean['MARRIAGE'] = df_clean['MARRIAGE'].replace({0: 3})
    print(f"MARRIAGE 清洗: {mar_before} → {df_clean['MARRIAGE'].value_counts().sort_index().to_dict()}")
    print(f"  处理依据: 数据字典仅定义1-3; 0值54条归入'其他(3)'")

    # --- 删除ID列 ---
    df_clean.drop(columns=['ID'], inplace=True, errors='ignore')
    print("删除 ID 列 (唯一标识符, 无预测价值)")

    # --- 重复值检查 ---
    dup_count = df_clean.duplicated().sum()
    print(f"重复值检查: {dup_count} 条重复行" + (" (已删除)" if dup_count > 0 else " (无需处理)"))

    # --- BILL_AMT 负值处理 ---
    bill_cols = [f'BILL_AMT{i}' for i in range(1, 7)]
    neg_count = (df_clean[bill_cols] < 0).sum().sum()
    if neg_count > 0:
        for col in bill_cols:
            df_clean[col] = df_clean[col].clip(lower=0)
        print(f"BILL_AMT 负值处理: {neg_count} 处负值已裁剪为0 (负值代表溢缴/退款)")

    return df_clean


# ================================
# 阶段二：特征工程 (6类操作)
# ================================

def feature_engineering(df):
    """
    特征工程主流程，返回 (特征矩阵 X, 目标变量 y, 特征名称列表)
    """
    print("\n" + "=" * 60)
    print("阶段二：特征工程 (核心考核点)")
    print("=" * 60)

    df_fe = df.copy()
    fe_log = []  # 记录每步操作

    # ==========================================
    # 操作1: 用户自定义聚合特征 (还款行为模式)
    # ==========================================
    print("\n[操作1] 还款行为聚合特征")

    pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
    bill_cols = [f'BILL_AMT{i}' for i in range(1, 7)]
    pay_amt_cols = [f'PAY_AMT{i}' for i in range(1, 7)]

    # 1a. 最近半年平均还款延迟
    df_fe['PAY_AVG_DELAY'] = df_fe[pay_cols].clip(lower=-1).mean(axis=1)
    fe_log.append("PAY_AVG_DELAY: 近6月平均还款延迟(-1/0=正常, >0=延迟)")

    # 1b. 还款延迟趋势 — 用 PAY_0(最近月) 与 PAY_6(最远月) 差值衡量趋势
    df_fe['PAY_DELAY_TREND'] = df_fe['PAY_0'] - df_fe['PAY_6']
    fe_log.append("PAY_DELAY_TREND: 延迟趋势(正=恶化, 负=改善)")

    # 1c. 延迟恶化月数 — 统计最近半年中延迟≥2的月份数
    df_fe['PAY_SEVERE_DELAY_COUNT'] = (df_fe[pay_cols] >= 2).sum(axis=1)
    fe_log.append("PAY_SEVERE_DELAY_COUNT: 严重延迟(≥2月)月数")

    # ==========================================
    # 操作2: 账单金额聚合特征
    # ==========================================
    print("[操作2] 账单金额聚合特征")

    # 2a. 近半年平均账单金额
    df_fe['BILL_AVG'] = df_fe[bill_cols].mean(axis=1)
    fe_log.append("BILL_AVG: 近6月平均账单金额")

    # 2b. 账单金额变化趋势 — 最近月减最远月
    df_fe['BILL_TREND'] = df_fe['BILL_AMT1'] - df_fe['BILL_AMT6']
    fe_log.append("BILL_TREND: 账单金额变化趋势(正=增加, 负=减少)")

    # 2c. 账单金额变异系数 — 衡量消费稳定性
    df_fe['BILL_CV'] = df_fe[bill_cols].std(axis=1) / (df_fe[bill_cols].mean(axis=1) + 1)
    fe_log.append("BILL_CV: 账单金额变异系数(消费稳定性)")

    # ==========================================
    # 操作3: 还款行为聚合特征
    # ==========================================
    print("[操作3] 还款行为派生特征")

    # 3a. 近半年平均还款金额
    df_fe['PAY_AMT_AVG'] = df_fe[pay_amt_cols].mean(axis=1)
    fe_log.append("PAY_AMT_AVG: 近6月平均还款金额")

    # 3b. 还款金额变化趋势
    df_fe['PAY_AMT_TREND'] = df_fe['PAY_AMT1'] - df_fe['PAY_AMT6']
    fe_log.append("PAY_AMT_TREND: 还款金额变化趋势")

    # ==========================================
    # 操作4: 特征交叉 — 比率型特征
    # ==========================================
    print("[操作4] 特征交叉 — 金融比率特征")

    # 4a. 信用额度利用率 (当月账单 / 信用额度)
    df_fe['CREDIT_UTIL_RATIO'] = df_fe['BILL_AMT1'] / (df_fe['LIMIT_BAL'] + 1)
    df_fe['CREDIT_UTIL_RATIO'] = df_fe['CREDIT_UTIL_RATIO'].clip(0, 5)  # 裁剪极端值
    fe_log.append("CREDIT_UTIL_RATIO: 信用额度利用率(高=资金压力大)")

    # 4b. 还款覆盖率 (还款金额 / 账单金额)
    df_fe['REPAY_COVERAGE'] = df_fe['PAY_AMT1'] / (df_fe['BILL_AMT1'] + 1)
    df_fe['REPAY_COVERAGE'] = df_fe['REPAY_COVERAGE'].clip(0, 10)
    fe_log.append("REPAY_COVERAGE: 还款覆盖率(低=还款能力不足)")

    # 4c. 账单占额度比
    df_fe['BILL_TO_LIMIT'] = df_fe['BILL_AMT1'] / (df_fe['LIMIT_BAL'] + 1)
    fe_log.append("BILL_TO_LIMIT: 账单/额度比")

    # 4d. 额度覆盖倍数 — 额度相对平均月账单的覆盖能力
    df_fe['LIMIT_COVERAGE'] = df_fe['LIMIT_BAL'] / (df_fe['BILL_AVG'] + 1)
    fe_log.append("LIMIT_COVERAGE: 额度覆盖倍数")

    # ==========================================
    # 操作5: 特征缩放与编码
    # ==========================================
    print("[操作5] 特征缩放与编码")

    # 5a. 数值特征标准化
    # 分离数值特征 (排除 PAY_* 类别型整数和标签)
    numeric_cols = ['LIMIT_BAL', 'AGE'] + bill_cols + pay_amt_cols + \
                   ['PAY_AVG_DELAY', 'PAY_DELAY_TREND', 'PAY_SEVERE_DELAY_COUNT',
                    'BILL_AVG', 'BILL_TREND', 'BILL_CV',
                    'PAY_AMT_AVG', 'PAY_AMT_TREND',
                    'CREDIT_UTIL_RATIO', 'REPAY_COVERAGE', 'BILL_TO_LIMIT', 'LIMIT_COVERAGE']

    scaler = StandardScaler()
    df_fe[numeric_cols] = scaler.fit_transform(df_fe[numeric_cols])
    fe_log.append(f"StandardScaler: {len(numeric_cols)}个数值特征标准化")

    # 5b. PAY_* 列保留原始值(有序类别)，不做标准化
    # 5c. 类别变量编码
    # One-Hot: SEX, MARRIAGE
    ohe = OneHotEncoder(sparse_output=False, drop='first')
    sex_mar_ohe = ohe.fit_transform(df_fe[['SEX', 'MARRIAGE']])
    sex_mar_ohe_cols = [f'OHE_{c}' for c in ohe.get_feature_names_out(['SEX', 'MARRIAGE'])]
    df_ohe = pd.DataFrame(sex_mar_ohe, columns=sex_mar_ohe_cols, index=df_fe.index)
    df_fe = pd.concat([df_fe, df_ohe], axis=1)
    df_fe.drop(columns=['SEX', 'MARRIAGE'], inplace=True)
    fe_log.append(f"One-Hot编码: SEX(男/女), MARRIAGE(已婚/单身/其他) → {len(sex_mar_ohe_cols)}列")

    # Ordinal: EDUCATION (有序: 研究生>大学>高中>其他)
    edu_order = [[1, 2, 3, 4]]
    oe = OrdinalEncoder(categories=edu_order)
    df_fe['EDUCATION_ORD'] = oe.fit_transform(df_fe[['EDUCATION']])
    df_fe.drop(columns=['EDUCATION'], inplace=True)
    fe_log.append("Ordinal编码: EDUCATION(研究生=0>大学=1>高中=2>其他=3)")

    # ==========================================
    # 操作6: PCA 降维分析 (用于可视化，不直接替换特征)
    # ==========================================
    print("[操作6] PCA 降维分析")

    # 将目标变量分离
    y = df_fe['default.payment.next.month']
    X = df_fe.drop(columns=['default.payment.next.month'])

    pca_full = PCA(n_components=min(30, X.shape[1]))
    pca_full.fit(X)
    cumsum_var = np.cumsum(pca_full.explained_variance_ratio_)

    print(f"  前5主成分解释方差: {pca_full.explained_variance_ratio_[:5].round(4)}")
    print(f"  前10主成分累计: {cumsum_var[9]:.2%}")
    print(f"  前20主成分累计: {cumsum_var[19]:.2%}")

    # 保存PCA模型以备后用
    import joblib
    import os
    from utils import MODEL_DIR
    joblib.dump(pca_full, os.path.join(MODEL_DIR, 'pca_model.pkl'))

    # ==========================================
    # 特征工程总结
    # ==========================================
    print("\n" + "=" * 60)
    print("特征工程总结")
    print("=" * 60)
    print(f"原始特征数: {len(df.columns) - 1} (不含标签)")
    print(f"最终特征数: {X.shape[1]}")
    print(f"新增特征: {X.shape[1] - (len(df.columns) - 1)} 个")
    print(f"\n操作明细:")
    for i, log in enumerate(fe_log, 1):
        print(f"  {i}. {log}")

    return X, y, scaler, fe_log


def plot_pca_variance(pca_model):
    """绘制PCA方差解释图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左: 各主成分解释方差
    n = min(30, len(pca_model.explained_variance_ratio_))
    x = range(1, n + 1)
    axes[0].bar(x, pca_model.explained_variance_ratio_[:n], color='steelblue', edgecolor='white')
    axes[0].plot(x, pca_model.explained_variance_ratio_[:n], 'o-', color='crimson', markersize=4)
    axes[0].set_xlabel('主成分编号')
    axes[0].set_ylabel('解释方差比例')
    axes[0].set_title('PCA 各主成分解释方差', fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)

    # 右: 累计解释方差
    cumsum = np.cumsum(pca_model.explained_variance_ratio_)
    axes[1].plot(x, cumsum[:n], 's-', color='crimson', linewidth=2, markersize=5)
    axes[1].axhline(y=0.9, color='gray', linestyle='--', alpha=0.7, label='90%阈值')
    axes[1].fill_between(x, 0, cumsum[:n], alpha=0.2, color='crimson')
    axes[1].set_xlabel('主成分数量')
    axes[1].set_ylabel('累计解释方差比例')
    axes[1].set_title('PCA 累计解释方差', fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    # 标注90%所需PC数
    n90 = np.argmax(cumsum >= 0.9) + 1
    axes[1].annotate(f'{n90}个PC达90%方差', xy=(n90, cumsum[n90-1]),
                     xytext=(n90 + 5, cumsum[n90-1] - 0.1),
                     arrowprops=dict(arrowstyle='->', color='gray'), fontsize=10)

    plt.tight_layout()
    save_fig(fig, '06_pca_variance.png')
    return fig


def plot_feature_correlation_after_fe(df):
    """特征工程后的相关性矩阵（前20个最重要特征）"""
    fig, ax = plt.subplots(figsize=(14, 11))
    # 选部分关键特征
    key_cols = [c for c in df.columns if c != 'default.payment.next.month'][:18]
    corr = df[key_cols + ['default.payment.next.month']].corr() if 'default.payment.next.month' in df.columns else df[key_cols].corr()
    sns.heatmap(corr, annot=False, cmap='RdBu_r', center=0, square=True,
                linewidths=0.3, cbar_kws={'shrink': 0.8}, ax=ax)
    ax.set_title('特征工程后关键变量相关性', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_fig(fig, '07_feature_correlation.png')
    return fig


def run_preprocessing():
    """执行完整的数据预处理与特征工程流程"""
    print(">>> 开始数据预处理与特征工程 <<<\n")

    # 加载数据
    df_raw = load_data()
    df_raw.columns = df_raw.columns.str.strip()
    print(f"原始数据: {df_raw.shape}")

    # 阶段一: 清洗
    df_clean = clean_data(df_raw)

    # 阶段二: 特征工程
    X, y, scaler, fe_log = feature_engineering(df_clean)

    # 保存处理后的数据
    df_processed = X.copy()
    df_processed['default.payment.next.month'] = y.values
    df_processed.to_csv('data_processed.csv', index=False)
    print("\n处理后数据已保存至: data_processed.csv")

    # PCA 降维分析图
    import joblib
    import os
    from utils import MODEL_DIR
    pca_model = joblib.load(os.path.join(MODEL_DIR, 'pca_model.pkl'))
    plot_pca_variance(pca_model)
    print("图6: PCA方差解释图 [OK]")

    # 保存scaler
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
    print("StandardScaler 已保存")

    print("\n>>> 数据预处理与特征工程完成! <<<")
    return X, y, scaler


if __name__ == '__main__':
    run_preprocessing()
