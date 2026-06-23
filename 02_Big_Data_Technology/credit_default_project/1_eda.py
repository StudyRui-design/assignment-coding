# -*- coding: utf-8 -*-
"""
1_eda.py — 数据读取与探索性分析模块
对信用卡违约数据集执行全面的描述性统计与可视化探索
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from utils import load_data, save_fig, FIG_DIR


def basic_info(df):
    """输出数据集基本概况"""
    print("=" * 60)
    print("数据集基本概况")
    print("=" * 60)
    print(f"数据形状: {df.shape[0]} 条样本 × {df.shape[1]} 个特征")
    print(f"\n特征列表:\n{df.dtypes}")
    print(f"\n重复行数: {df.duplicated().sum()}")
    print(f"\n缺失值统计:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({'缺失数': missing, '缺失率(%)': missing_pct})
    print(missing_df[missing_df['缺失数'] > 0] if missing_df['缺失数'].sum() > 0 else "无缺失值")

    print(f"\n描述性统计:")
    print(df.describe().round(2).to_string())
    return df.describe()


def check_data_quality(df):
    """检测数据质量问题"""
    print("\n" + "=" * 60)
    print("数据质量问题检测")
    print("=" * 60)

    issues = {}

    # 1. EDUCATION 类别分布（预期1-4，实际含0/5/6）
    edu_dist = df['EDUCATION'].value_counts().sort_index()
    print(f"EDUCATION 类别分布: {edu_dist.to_dict()}")
    issues['EDUCATION异常值'] = {
        '0': int((df['EDUCATION'] == 0).sum()),
        '5': int((df['EDUCATION'] == 5).sum()),
        '6': int((df['EDUCATION'] == 6).sum())
    }

    # 2. MARRIAGE 类别分布（预期1-3，实际含0）
    mar_dist = df['MARRIAGE'].value_counts().sort_index()
    print(f"MARRIAGE 类别分布: {mar_dist.to_dict()}")
    issues['MARRIAGE异常值'] = {'0': int((df['MARRIAGE'] == 0).sum())}

    # 3. 目标变量类别不平衡
    target_dist = df['default.payment.next.month'].value_counts(normalize=True)
    print(f"目标变量分布: 不违约={target_dist[0]:.1%}, 违约={target_dist[1]:.1%}")
    print(f"类别不平衡比: {target_dist[0]/target_dist[1]:.2f}:1")
    issues['类别不平衡'] = f"{target_dist[0]/target_dist[1]:.2f}:1"

    # 4. 异常值检测 (IQR方法，仅对数值金额字段)
    amount_cols = ['LIMIT_BAL'] + [f'BILL_AMT{i}' for i in range(1, 7)] + [f'PAY_AMT{i}' for i in range(1, 7)]
    outlier_counts = {}
    for col in amount_cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        if n_outliers > 0:
            outlier_counts[col] = n_outliers
    print(f"各金额字段异常值数量(IQR): {outlier_counts}")

    return issues


def plot_numeric_distributions(df):
    """绘制数值变量分布直方图"""
    numeric_cols = ['LIMIT_BAL', 'AGE']
    bill_cols = [f'BILL_AMT{i}' for i in range(1, 7)]
    pay_amt_cols = [f'PAY_AMT{i}' for i in range(1, 7)]

    # 图1: LIMIT_BAL + AGE + 关键账单/还款
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    plot_cols = ['LIMIT_BAL', 'AGE', 'BILL_AMT1', 'BILL_AMT6', 'PAY_AMT1', 'PAY_AMT6']
    titles = ['信用额度分布', '年龄分布',
              '近1月账单金额', '近6月账单金额',
              '近1月还款金额', '近6月还款金额']
    for ax, col, title in zip(axes.flat, plot_cols, titles):
        ax.hist(df[col], bins=60, color='steelblue', edgecolor='white', alpha=0.85)
        ax.axvline(df[col].median(), color='crimson', linestyle='--', linewidth=1.5, label=f'中位数={df[col].median():.0f}')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('频数')
        ax.legend(fontsize=8)
    fig.suptitle('关键数值特征分布直方图', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig(fig, '01_numeric_distributions.png')
    return fig


def plot_categorical_distributions(df):
    """绘制类别变量分布柱状图"""
    cat_cols = ['SEX', 'EDUCATION', 'MARRIAGE']
    cat_labels = {
        'SEX': {1: '男', 2: '女'},
        'EDUCATION': {0: '未知', 1: '研究生', 2: '大学', 3: '高中', 4: '其他', 5: '未知5', 6: '未知6'},
        'MARRIAGE': {0: '未知', 1: '已婚', 2: '单身', 3: '其他'}
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, col in zip(axes, cat_cols):
        counts = df[col].value_counts().sort_index()
        labels = [cat_labels[col].get(k, str(k)) for k in counts.index]
        colors = sns.color_palette("Set2", n_colors=len(counts))
        bars = ax.bar(range(len(counts)), counts.values, color=colors, edgecolor='white')
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=9)
        ax.set_title(f'{col} 分布', fontsize=12, fontweight='bold')
        ax.set_ylabel('样本数')
        # 添加数值标签
        for bar, v in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50, str(v),
                    ha='center', fontsize=8)
    fig.suptitle('类别变量分布柱状图', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_fig(fig, '02_categorical_distributions.png')
    return fig


def plot_correlation_heatmap(df):
    """绘制数值特征相关性热力图"""
    numeric_cols = ['LIMIT_BAL', 'AGE'] + \
                   [f'PAY_{i}' for i in ['0', '2', '3', '4', '5', '6']] + \
                   [f'BILL_AMT{i}' for i in range(1, 7)] + \
                   [f'PAY_AMT{i}' for i in range(1, 7)]
    corr_matrix = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(16, 13))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
                cbar_kws={'shrink': 0.8}, ax=ax)
    ax.set_title('数值特征皮尔逊相关系数热力图', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    save_fig(fig, '03_correlation_heatmap.png')
    return fig


def plot_target_analysis(df):
    """目标变量分析"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 子图1: 违约 vs 非违约 饼图
    labels = ['正常还款', '违约']
    sizes = df['default.payment.next.month'].value_counts().values
    colors_pie = ['#5DADE2', '#E74C3C']
    explode = (0, 0.08)
    wedges, texts, autotexts = axes[0].pie(
        sizes, explode=explode, labels=labels, colors=colors_pie,
        autopct='%1.1f%%', shadow=True, startangle=90,
        textprops={'fontsize': 12})
    for at in autotexts:
        at.set_fontweight('bold')
    axes[0].set_title('目标变量(违约)分布', fontsize=13, fontweight='bold')

    # 子图2: 按违约分组的各数值特征均值比较
    compare_features = ['LIMIT_BAL', 'AGE', 'PAY_0', 'BILL_AMT1', 'PAY_AMT1']
    compare_labels = ['信用额度', '年龄', '最近还款状态', '近1月账单', '近1月还款']
    group_mean = df.groupby('default.payment.next.month')[compare_features].mean()

    x = np.arange(len(compare_features))
    width = 0.35
    bars1 = axes[1].bar(x - width/2, group_mean.loc[0], width, label='正常还款', color='#5DADE2', edgecolor='white')
    bars2 = axes[1].bar(x + width/2, group_mean.loc[1], width, label='违约', color='#E74C3C', edgecolor='white')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(compare_labels, fontsize=10)
    axes[1].set_ylabel('均值')
    axes[1].set_title('不同还款状态特征均值对比', fontsize=13, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save_fig(fig, '04_target_analysis.png')
    return fig


def plot_business_insights(df):
    """业务关系洞察图表"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # 1. 信用额度 vs 违约
    for status, label, color in [(0, '正常还款', '#5DADE2'), (1, '违约', '#E74C3C')]:
        subset = df[df['default.payment.next.month'] == status]['LIMIT_BAL']
        axes[0, 0].hist(subset, bins=40, alpha=0.6, label=label, color=color, edgecolor='white')
    axes[0, 0].set_title('信用额度与违约关系', fontweight='bold')
    axes[0, 0].set_xlabel('信用额度(NTD)')
    axes[0, 0].legend()

    # 2. 年龄 vs 违约
    for status, label, color in [(0, '正常还款', '#5DADE2'), (1, '违约', '#E74C3C')]:
        subset = df[df['default.payment.next.month'] == status]['AGE']
        axes[0, 1].hist(subset, bins=30, alpha=0.6, label=label, color=color, edgecolor='white')
    axes[0, 1].set_title('年龄与违约关系', fontweight='bold')
    axes[0, 1].set_xlabel('年龄')
    axes[0, 1].legend()

    # 3. 还款状态 vs 违约
    pay_default = df.groupby('PAY_0')['default.payment.next.month'].mean() * 100
    axes[0, 2].bar(pay_default.index.astype(str), pay_default.values, color='steelblue', edgecolor='white')
    axes[0, 2].set_title('还款延迟状态与违约率关系', fontweight='bold')
    axes[0, 2].set_xlabel('最近还款状态(-2=无消费,-1=按时,0+=延迟月数)')
    axes[0, 2].set_ylabel('违约率(%)')

    # 4. 教育水平 vs 违约率
    edu_default = df.groupby('EDUCATION')['default.payment.next.month'].mean() * 100
    edu_labels = {0: '未知', 1: '研究生', 2: '大学', 3: '高中', 4: '其他', 5: '未知5', 6: '未知6'}
    axes[1, 0].bar([edu_labels.get(k, str(k)) for k in edu_default.index],
                   edu_default.values, color='steelblue', edgecolor='white')
    axes[1, 0].set_title('教育水平与违约率关系', fontweight='bold')
    axes[1, 0].set_ylabel('违约率(%)')
    axes[1, 0].tick_params(axis='x', rotation=30)

    # 5. 婚姻状态 vs 违约率
    mar_default = df.groupby('MARRIAGE')['default.payment.next.month'].mean() * 100
    mar_labels = {0: '未知', 1: '已婚', 2: '单身', 3: '其他'}
    axes[1, 1].bar([mar_labels.get(k, str(k)) for k in mar_default.index],
                   mar_default.values, color='steelblue', edgecolor='white')
    axes[1, 1].set_title('婚姻状态与违约率关系', fontweight='bold')
    axes[1, 1].set_ylabel('违约率(%)')

    # 6. 按月还款状态分组的违约率趋势
    pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
    pay_labels = ['9月', '8月', '7月', '6月', '5月', '4月']
    avg_delay_by_month = []
    for col in pay_cols:
        avg_delay_by_month.append(df[df['default.payment.next.month'] == 1][col].mean())
    avg_delay_normal = []
    for col in pay_cols:
        avg_delay_normal.append(df[df['default.payment.next.month'] == 0][col].mean())

    axes[1, 2].plot(pay_labels, avg_delay_by_month, 'o-', color='#E74C3C', linewidth=2, label='违约组平均延迟')
    axes[1, 2].plot(pay_labels, avg_delay_normal, 's-', color='#5DADE2', linewidth=2, label='正常组平均延迟')
    axes[1, 2].set_title('历史还款延迟趋势对比', fontweight='bold')
    axes[1, 2].set_ylabel('平均还款延迟状态')
    axes[1, 2].legend(fontsize=9)
    axes[1, 2].grid(alpha=0.3)

    fig.suptitle('业务洞察：客户属性与信用卡违约关系分析', fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig(fig, '05_business_insights.png')
    return fig


def run_eda():
    """执行完整的探索性分析流程"""
    print(">>> 开始探索性数据分析 (EDA) <<<")
    df = load_data()
    df.columns = df.columns.str.strip()

    # 1 基本概况
    basic_info(df)

    # 2 数据质量检测
    issues = check_data_quality(df)

    # 3 数值变量分布
    plot_numeric_distributions(df)
    print("图1: 数值变量分布直方图 [OK]")

    # 4 类别变量分布
    plot_categorical_distributions(df)
    print("图2: 类别变量分布柱状图 [OK]")

    # 5 相关性热力图
    plot_correlation_heatmap(df)
    print("图3: 相关性热力图 [OK]")

    # 6 目标变量分析
    plot_target_analysis(df)
    print("图4: 目标变量分析图 [OK]")

    # 7 业务洞察
    plot_business_insights(df)
    print("图5: 业务关系洞察图 [OK]")

    print("\n>>> EDA 完成! 所有图表已保存至 figures/ 目录 <<<")
    return df, issues


if __name__ == '__main__':
    run_eda()
