# -*- coding: utf-8 -*-
"""
5_app.py — 可视化应用界面 (Streamlit Web应用)
信用卡违约预测系统 — 交互式数据挖掘成果展示
启动方式: streamlit run 5_app.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互后端，支持无GUI环境生成图表
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import joblib
import warnings

warnings.filterwarnings('ignore')

# ============================
# 健壮的中文字体配置（多平台支持）
# ============================

def _register_cjk_fonts():
    """向 fontManager 注册中文字体文件"""
    simhei_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')
    if os.path.exists(simhei_path):
        try:
            fm.fontManager.addfont(simhei_path)
        except Exception:
            pass


def _setup_chinese_font():
    """
    配置中文字体，支持 Windows / Linux / macOS 多平台。
    必须在 sns.set_style() 之后调用，因为 seaborn 会重置 font.sans-serif。
    """
    _CJK_FONT_CANDIDATES = [
        'SimHei', 'Microsoft YaHei', 'STXihei',
        'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
        'Noto Sans CJK SC', 'Noto Sans SC',
        'PingFang SC', 'Heiti SC', 'STHeiti',
        'Arial Unicode MS',
    ]
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    for font_name in _CJK_FONT_CANDIDATES:
        if font_name in available_fonts:
            plt.rcParams['font.sans-serif'] = [font_name] + \
                [f for f in plt.rcParams['font.sans-serif'] if f != font_name]
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            return
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    print("[警告] 未找到中文字体，图表中文可能无法正常显示", file=sys.stderr)


# 第一步：注册字体文件
_register_cjk_fonts()
# 第二步：设置 seaborn 风格（会重置部分 rcParams）
sns.set_style("whitegrid")
sns.set_palette("Set2")
# 第三步：在 sns 之后覆盖字体设置（关键！seaborn 会重置 font.sans-serif）
_setup_chinese_font()

import streamlit as st

# ============================
# 页面配置
# ============================
st.set_page_config(
    page_title="信用卡违约预测系统",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
FIG_DIR = os.path.join(BASE_DIR, 'figures')


# ============================
# 加载资源
# ============================

@st.cache_resource
def load_resources():
    """加载模型与数据（使用缓存避免重复加载）"""
    resources = {}
    try:
        resources['tuned_model'] = joblib.load(os.path.join(MODEL_DIR, 'tuned_model.pkl'))
    except:
        try:
            resources['tuned_model'] = joblib.load(os.path.join(MODEL_DIR, 'best_model.pkl'))
        except:
            resources['tuned_model'] = None

    try:
        resources['scaler'] = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
    except:
        resources['scaler'] = None

    # 加载数据
    try:
        resources['df_raw'] = pd.read_csv(os.path.join(BASE_DIR, 'data.csv'))
        resources['df_raw'].columns = resources['df_raw'].columns.str.strip()
    except:
        resources['df_raw'] = None

    try:
        resources['df_processed'] = pd.read_csv(os.path.join(BASE_DIR, 'data_processed.csv'))
    except:
        resources['df_processed'] = None

    try:
        resources['model_comparison'] = pd.read_csv(os.path.join(MODEL_DIR, 'model_comparison.csv'), index_col=0)
    except:
        resources['model_comparison'] = None

    return resources


# ============================
# 辅助函数
# ============================

def load_image(name):
    """加载保存的图表"""
    path = os.path.join(FIG_DIR, name)
    if os.path.exists(path):
        return path
    return None


# ============================
# 主应用
# ============================

def main():
    # ---- 侧边栏 ----
    st.sidebar.title("💳 信用卡违约预测系统")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**数据挖掘实验 · 期末考核**")
    st.sidebar.markdown("数据集: Default of Credit Card Clients")
    st.sidebar.markdown("来源: Kaggle / UCI Machine Learning Repository")
    st.sidebar.markdown("---")

    # 页面导航
    page = st.sidebar.radio(
        "📋 功能导航",
        ["🏠 数据概览", "📊 探索性分析", "📈 模型评估", "🔮 在线预测"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**数据集概况**\n\n"
        "- 样本量: 30,000 条\n"
        "- 特征数: 25 列\n"
        "- 目标: 下月是否违约\n"
        "- 违约率: 22.12%\n"
        "- 时间窗口: 2005年4月-9月"
    )

    # 加载资源
    resources = load_resources()

    # ================================
    # 页面1: 数据概览
    # ================================
    if page == "🏠 数据概览":
        st.title("🏠 数据概览")
        st.markdown("展示信用卡违约数据集的整体情况，包括数据表预览、统计摘要与数据质量概况。")

        if resources['df_raw'] is not None:
            df = resources['df_raw']

            # 基本统计卡片
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("样本总数", f"{df.shape[0]:,}")
            col2.metric("特征数量", str(df.shape[1]))
            col3.metric("违约样本", f"{(df['default.payment.next.month']==1).sum():,}",
                        f"{(df['default.payment.next.month']==1).mean():.1%}")
            col4.metric("正常样本", f"{(df['default.payment.next.month']==0).sum():,}",
                        f"{(df['default.payment.next.month']==0).mean():.1%}")

            st.markdown("---")

            # 数据表预览
            tab1, tab2, tab3 = st.tabs(["📋 数据表预览", "📊 描述性统计", "🔍 数据质量"])

            with tab1:
                st.subheader("原始数据前20行")
                st.dataframe(df.head(20), width='stretch')

                st.subheader("数据类型与缺失值")
                dtype_df = pd.DataFrame({
                    '数据类型': df.dtypes.astype(str),
                    '缺失值': df.isnull().sum(),
                    '唯一值数': df.nunique()
                })
                st.dataframe(dtype_df, width='stretch')

            with tab2:
                st.subheader("数值特征描述性统计")
                st.dataframe(df.describe().round(2), width='stretch')

                st.markdown("**特征说明:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(
                        "- **LIMIT_BAL**: 信用额度 (NTD)\n"
                        "- **SEX**: 性别 (1=男, 2=女)\n"
                        "- **EDUCATION**: 教育 (1=研究生,2=大学,3=高中,4=其他)\n"
                        "- **MARRIAGE**: 婚姻 (1=已婚,2=单身,3=其他)\n"
                        "- **AGE**: 年龄"
                    )
                with col_b:
                    st.markdown(
                        "- **PAY_0~PAY_6**: 还款延迟状态 (-2=无消费,-1=按时,0+=延迟月数)\n"
                        "- **BILL_AMT1~6**: 账单金额 (NTD)\n"
                        "- **PAY_AMT1~6**: 还款金额 (NTD)\n"
                        "- **default**: 下月是否违约 (0=否, 1=是)"
                    )

            with tab3:
                st.subheader("数据质量问题")
                st.markdown("""
                | 问题项 | 详情 | 严重程度 |
                |--------|------|----------|
                | EDUCATION异常值 | 含0(14条)、5(280条)、6(51条) 未文档化类别 | 🟡 中 |
                | MARRIAGE异常值 | 含0(54条) 未定义类别 | 🟢 低 |
                | 类别不平衡 | 违约:不违约 ≈ 1:3.5 | 🟡 中 |
                | 金额字段极端值 | BILL_AMT/PAY_AMT 含极端高值 | 🟡 中 |
                """)

        else:
            st.error("未找到数据文件，请确保 data.csv 存在于项目根目录。")

    # ================================
    # 页面2: 探索性分析
    # ================================
    elif page == "📊 探索性分析":
        st.title("📊 探索性分析")
        st.markdown("通过可视化手段探索数据分布、变量关系与业务规律。")

        tabs = st.tabs(["📈 特征分布", "🔥 相关性分析", "🎯 目标分析", "💡 业务洞察"])

        with tabs[0]:
            st.subheader("数值特征分布")
            img1 = load_image('01_numeric_distributions.png')
            if img1:
                st.image(img1, width='stretch')
            else:
                st.warning("图表尚未生成，请先运行 1_eda.py")

            st.subheader("类别特征分布")
            img2 = load_image('02_categorical_distributions.png')
            if img2:
                st.image(img2, width='stretch')

        with tabs[1]:
            st.subheader("皮尔逊相关系数热力图")
            img3 = load_image('03_correlation_heatmap.png')
            if img3:
                st.image(img3, width='stretch')

            st.markdown("""
            **关键发现:**
            - 各月 BILL_AMT 之间高度正相关 (0.85~0.95)，客户消费习惯稳定
            - 各月 PAY_AMT 之间中等正相关 (0.5~0.7)
            - 各月 PAY_* 之间正相关 (0.6~0.8)，还款行为具有持续性
            - LIMIT_BAL 与 BILL_AMT 呈中等正相关，额度高者消费也高
            """)

        with tabs[2]:
            st.subheader("目标变量分析")
            img4 = load_image('04_target_analysis.png')
            if img4:
                st.image(img4, width='stretch')

        with tabs[3]:
            st.subheader("业务关系洞察")
            img5 = load_image('05_business_insights.png')
            if img5:
                st.image(img5, width='stretch')

            st.markdown("""
            **业务洞察总结:**
            1. **还款状态是最强信号**: PAY_0≥2 的客户违约率显著升高
            2. **新近违约趋势明显**: 违约组近半年的还款延迟整体呈上升态势
            3. **教育水平差异**: 低教育水平客户违约率略高
            4. **婚姻状态**: 单身客户违约率相对较高
            """)

    # ================================
    # 页面3: 模型评估
    # ================================
    elif page == "📈 模型评估":
        st.title("📈 模型评估")
        st.markdown("多模型对比实验结果与评估指标展示。")

        if resources['model_comparison'] is not None:
            comp_df = resources['model_comparison']

            # 性能对比表格
            st.subheader("模型性能对比表 (测试集)")
            # 高亮最优值
            styled_df = comp_df.style.format("{:.4f}").highlight_max(
                subset=['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC-ROC'],
                color='#90EE90', axis=0
            )
            st.dataframe(styled_df, width='stretch')

            # 找出最优模型
            best_f1_model = comp_df['F1-Score'].idxmax()
            best_auc_model = comp_df['AUC-ROC'].idxmax()
            col1, col2 = st.columns(2)
            col1.success(f"🏆 最优 F1-Score: **{best_f1_model}** ({comp_df.loc[best_f1_model, 'F1-Score']:.4f})")
            col2.info(f"🎯 最优 AUC-ROC: **{best_auc_model}** ({comp_df.loc[best_auc_model, 'AUC-ROC']:.4f})")

            st.markdown("---")

            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("ROC 曲线对比")
                img8 = load_image('08_roc_curves.png')
                if img8:
                    st.image(img8, width='stretch')

                st.subheader("性能雷达图")
                img11 = load_image('11_radar_chart.png')
                if img11:
                    st.image(img11, width='stretch')

            with col_right:
                st.subheader("性能柱状对比图")
                img9 = load_image('09_performance_comparison.png')
                if img9:
                    st.image(img9, width='stretch')

                st.subheader("特征重要性排序")
                img10 = load_image('10_feature_importance.png')
                if img10:
                    st.image(img10, width='stretch')

            # 调优对比
            st.markdown("---")
            st.subheader("超参数调优效果")
            img13 = load_image('13_tuning_comparison.png')
            if img13:
                st.image(img13, width='stretch')
            img12 = load_image('12_grid_search_heatmap.png')
            if img12:
                st.image(img12, width='stretch')
        else:
            st.warning("模型评估结果尚未生成，请先运行 3_modeling.py 和 4_tuning.py")

    # ================================
    # 页面4: 在线预测
    # ================================
    elif page == "🔮 在线预测":
        st.title("🔮 在线违约预测")
        st.markdown("输入客户基本信息与账户数据，系统将实时返回违约预测结果。")

        model = resources['tuned_model']
        if model is None:
            st.error("❌ 未找到训练好的模型！请先运行训练脚本。")
            return

        # 输入表单
        with st.form("prediction_form"):
            st.markdown("### 📝 客户信息输入")

            col1, col2, col3 = st.columns(3)

            with col1:
                limit_bal = st.number_input("信用额度 (NTD)", min_value=10000, max_value=1000000,
                                            value=200000, step=10000, format="%d")
                sex = st.selectbox("性别", options=["男", "女"], index=1)
                education = st.selectbox("教育水平", options=["研究生", "大学", "高中", "其他"], index=1)
                marriage = st.selectbox("婚姻状态", options=["已婚", "单身", "其他"], index=0)
                age = st.slider("年龄", min_value=21, max_value=80, value=35)

            with col2:
                st.markdown("**还款延迟状态 (近6月)**")
                st.caption("-2=无消费, -1=按时还款, 0+=延迟月数")
                pay_0 = st.selectbox("最近月(9月) PAY_0", options=list(range(-2, 9)), index=0,
                                     format_func=lambda x: f"{x} ({'无消费' if x==-2 else '按时' if x==-1 else f'延迟{x}月'})")
                pay_2 = st.selectbox("前1月(8月) PAY_2", options=list(range(-2, 9)), index=0)
                pay_3 = st.selectbox("前2月(7月) PAY_3", options=list(range(-2, 9)), index=0)
                pay_4 = st.selectbox("前3月(6月) PAY_4", options=list(range(-2, 9)), index=0)
                pay_5 = st.selectbox("前4月(5月) PAY_5", options=list(range(-2, 9)), index=0)
                pay_6 = st.selectbox("前5月(4月) PAY_6", options=list(range(-2, 9)), index=0)

            with col3:
                st.markdown("**账单金额 (NTD, 近6月)**")
                bill_amt1 = st.number_input("近1月账单", min_value=-200000, max_value=1000000, value=50000, step=1000)
                bill_amt2 = st.number_input("近2月账单", min_value=-200000, max_value=1000000, value=45000, step=1000)
                bill_amt3 = st.number_input("近3月账单", min_value=-200000, max_value=1000000, value=40000, step=1000)
                bill_amt4 = st.number_input("近4月账单", min_value=-200000, max_value=1000000, value=38000, step=1000)
                bill_amt5 = st.number_input("近5月账单", min_value=-200000, max_value=1000000, value=35000, step=1000)
                bill_amt6 = st.number_input("近6月账单", min_value=-200000, max_value=1000000, value=30000, step=1000)

                st.markdown("**还款金额 (NTD, 近6月)**")
                pay_amt1 = st.number_input("近1月还款", min_value=0, max_value=1000000, value=10000, step=1000)
                pay_amt2 = st.number_input("近2月还款", min_value=0, max_value=1000000, value=9000, step=1000)
                pay_amt3 = st.number_input("近3月还款", min_value=0, max_value=1000000, value=8000, step=1000)
                pay_amt4 = st.number_input("近4月还款", min_value=0, max_value=1000000, value=7000, step=1000)
                pay_amt5 = st.number_input("近5月还款", min_value=0, max_value=1000000, value=6000, step=1000)
                pay_amt6 = st.number_input("近6月还款", min_value=0, max_value=1000000, value=5000, step=1000)

            submitted = st.form_submit_button("🚀 开始预测", type="primary", width='stretch')

        if submitted:
            # 构建输入特征
            input_data = build_input_features(
                limit_bal, sex, education, marriage, age,
                pay_0, pay_2, pay_3, pay_4, pay_5, pay_6,
                bill_amt1, bill_amt2, bill_amt3, bill_amt4, bill_amt5, bill_amt6,
                pay_amt1, pay_amt2, pay_amt3, pay_amt4, pay_amt5, pay_amt6
            )

            # 进行预测
            with st.spinner("正在分析客户风险..."):
                try:
                    # 尝试获取概率
                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(input_data)[0, 1]
                        prediction = 1 if proba > 0.5 else 0
                    else:
                        prediction = model.predict(input_data)[0]
                        proba = float(prediction)

                    # 风险等级
                    if proba < 0.2:
                        risk_level = "🟢 低风险"
                        risk_color = "green"
                        suggestion = "该客户还款表现良好，建议维持现有信用策略。"
                    elif proba < 0.4:
                        risk_level = "🟡 中等风险"
                        risk_color = "orange"
                        suggestion = "客户有一定违约倾向，建议适当关注并发送还款提醒。"
                    elif proba < 0.6:
                        risk_level = "🟠 较高风险"
                        risk_color = "darkorange"
                        suggestion = "建议降低信用额度或提前沟通，了解客户还款困难原因。"
                    else:
                        risk_level = "🔴 高风险"
                        risk_color = "red"
                        suggestion = "强烈建议立即联系客户，重新评估信用策略，考虑冻结额度。"
                except Exception as e:
                    st.error(f"预测失败: {e}")
                    st.info("请确保已运行完整的训练流程 (1_eda.py → 2_preprocessing.py → 3_modeling.py → 4_tuning.py)")
                    return

            # 显示结果
            st.markdown("---")
            st.markdown("### 📊 预测结果")

            res_col1, res_col2 = st.columns([1, 2])

            with res_col1:
                # 仪表盘样式
                fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=False))
                theta = np.linspace(0, 2 * np.pi, 100)
                # 背景圆
                ax.fill_between(np.linspace(-1, 1, 100), -1, 1, alpha=0.05, color='gray')
                # 简易仪表盘
                import matplotlib.patches as mpatches
                wedge_colors = ['#27AE60', '#F1C40F', '#E67E22', '#E74C3C']
                wedges = [
                    mpatches.Wedge((0, 0), 1, 0, 72, width=0.3, color=wedge_colors[0], alpha=0.6),
                    mpatches.Wedge((0, 0), 1, 72, 144, width=0.3, color=wedge_colors[1], alpha=0.6),
                    mpatches.Wedge((0, 0), 1, 144, 216, width=0.3, color=wedge_colors[2], alpha=0.6),
                    mpatches.Wedge((0, 0), 1, 216, 360, width=0.3, color=wedge_colors[3], alpha=0.6),
                ]
                for w in wedges:
                    ax.add_patch(w)
                # 指针
                needle_angle = 360 - proba * 360
                needle_rad = np.radians(needle_angle)
                ax.arrow(0, 0, 0.6 * np.cos(needle_rad), 0.6 * np.sin(needle_rad),
                         head_width=0.08, head_length=0.1, fc='black', ec='black')
                ax.set_xlim(-1.2, 1.2)
                ax.set_ylim(-1.2, 1.2)
                ax.set_aspect('equal')
                ax.axis('off')
                ax.text(0, -0.35, f'{proba:.1%}', ha='center', fontsize=20, fontweight='bold')
                ax.text(0, -0.55, '违约概率', ha='center', fontsize=10, color='gray')
                st.pyplot(fig)

                st.markdown(f"### {risk_level}")
                st.metric("预测结果", "⚠️ 可能违约" if prediction == 1 else "✅ 正常还款")
                st.metric("违约概率", f"{proba:.2%}")

            with res_col2:
                st.markdown("#### 💡 风险建议")
                st.info(suggestion)

                st.markdown("#### 📋 风险评估明细")
                risk_factors = analyze_risk_factors(
                    pay_0, pay_2, pay_3, pay_4, pay_5, pay_6,
                    limit_bal, bill_amt1, pay_amt1
                )
                for factor in risk_factors:
                    icon = "⚠️" if factor['risk'] == 'high' else "⚡" if factor['risk'] == 'medium' else "✅"
                    st.markdown(f"{icon} **{factor['name']}**: {factor['detail']}")


def build_input_features(limit_bal, sex, education, marriage, age,
                         pay_0, pay_2, pay_3, pay_4, pay_5, pay_6,
                         bill_amt1, bill_amt2, bill_amt3, bill_amt4, bill_amt5, bill_amt6,
                         pay_amt1, pay_amt2, pay_amt3, pay_amt4, pay_amt5, pay_amt6):
    """
    根据用户输入构建特征矩阵。
    注意：需要与训练时的特征工程保持完全一致。
    """
    # 构建原始特征DataFrame
    sex_val = 1 if sex == "男" else 2
    edu_map = {"研究生": 1, "大学": 2, "高中": 3, "其他": 4}
    mar_map = {"已婚": 1, "单身": 2, "其他": 3}
    education_val = edu_map[education]
    marriage_val = mar_map[marriage]

    raw = pd.DataFrame([{
        'LIMIT_BAL': limit_bal,
        'SEX': sex_val,
        'EDUCATION': education_val,
        'MARRIAGE': marriage_val,
        'AGE': age,
        'PAY_0': pay_0, 'PAY_2': pay_2, 'PAY_3': pay_3,
        'PAY_4': pay_4, 'PAY_5': pay_5, 'PAY_6': pay_6,
        'BILL_AMT1': bill_amt1, 'BILL_AMT2': bill_amt2, 'BILL_AMT3': bill_amt3,
        'BILL_AMT4': bill_amt4, 'BILL_AMT5': bill_amt5, 'BILL_AMT6': bill_amt6,
        'PAY_AMT1': pay_amt1, 'PAY_AMT2': pay_amt2, 'PAY_AMT3': pay_amt3,
        'PAY_AMT4': pay_amt4, 'PAY_AMT5': pay_amt5, 'PAY_AMT6': pay_amt6,
    }])

    # 特征工程 (与 2_preprocessing.py 保持一致)
    pay_cols = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
    bill_cols = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
    pay_amt_cols = ['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']

    raw['PAY_AVG_DELAY'] = raw[pay_cols].clip(lower=-1).mean(axis=1)
    raw['PAY_DELAY_TREND'] = raw['PAY_0'] - raw['PAY_6']
    raw['PAY_SEVERE_DELAY_COUNT'] = (raw[pay_cols] >= 2).sum(axis=1)
    raw['BILL_AVG'] = raw[bill_cols].mean(axis=1)
    raw['BILL_TREND'] = raw['BILL_AMT1'] - raw['BILL_AMT6']
    raw['BILL_CV'] = raw[bill_cols].std(axis=1) / (raw[bill_cols].mean(axis=1) + 1)
    raw['PAY_AMT_AVG'] = raw[pay_amt_cols].mean(axis=1)
    raw['PAY_AMT_TREND'] = raw['PAY_AMT1'] - raw['PAY_AMT6']
    raw['CREDIT_UTIL_RATIO'] = (raw['BILL_AMT1'] / (raw['LIMIT_BAL'] + 1)).clip(0, 5)
    raw['REPAY_COVERAGE'] = (raw['PAY_AMT1'] / (raw['BILL_AMT1'] + 1)).clip(0, 10)
    raw['BILL_TO_LIMIT'] = raw['BILL_AMT1'] / (raw['LIMIT_BAL'] + 1)
    raw['LIMIT_COVERAGE'] = raw['LIMIT_BAL'] / (raw['BILL_AVG'] + 1)

    # 加载scaler并标准化
    import joblib
    try:
        scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
        numeric_cols = ['LIMIT_BAL', 'AGE'] + bill_cols + pay_amt_cols + \
                       ['PAY_AVG_DELAY', 'PAY_DELAY_TREND', 'PAY_SEVERE_DELAY_COUNT',
                        'BILL_AVG', 'BILL_TREND', 'BILL_CV',
                        'PAY_AMT_AVG', 'PAY_AMT_TREND',
                        'CREDIT_UTIL_RATIO', 'REPAY_COVERAGE', 'BILL_TO_LIMIT', 'LIMIT_COVERAGE']
        raw[numeric_cols] = scaler.transform(raw[numeric_cols])
    except:
        pass  # Scaler不可用，跳过

    # One-Hot编码
    # SEX: 男=1,女=2 → drop first (1) → 女性=1
    raw['OHE_SEX_2'] = 1 if sex_val == 2 else 0
    # MARRIAGE: 1=已婚,2=单身,3=其他 → drop first (1) → OHE_MARRIAGE_2, OHE_MARRIAGE_3
    raw['OHE_MARRIAGE_2'] = 1 if marriage_val == 2 else 0
    raw['OHE_MARRIAGE_3'] = 1 if marriage_val == 3 else 0

    # Ordinal: EDUCATION (研究生=0,大学=1,高中=2,其他=3)
    edu_ord_map = {1: 0, 2: 1, 3: 2, 4: 3}
    raw['EDUCATION_ORD'] = edu_ord_map[education_val]

    # 移除原始类别列
    raw.drop(columns=['SEX', 'MARRIAGE'], inplace=True)
    if 'EDUCATION' in raw.columns:
        raw.drop(columns=['EDUCATION'], inplace=True)

    return raw


def analyze_risk_factors(pay_0, pay_2, pay_3, pay_4, pay_5, pay_6,
                          limit_bal, bill_amt1, pay_amt1):
    """分析用户风险因素"""
    factors = []

    # 还款延迟风险
    avg_delay = np.mean([max(p, -1) for p in [pay_0, pay_2, pay_3, pay_4, pay_5, pay_6]])
    if pay_0 >= 2:
        factors.append({'name': '最近还款严重延迟', 'risk': 'high',
                        'detail': f'最近月延迟{pay_0}个月，是违约的强信号'})
    elif pay_0 >= 1:
        factors.append({'name': '最近还款轻微延迟', 'risk': 'medium',
                        'detail': '最近月有轻微延迟，需关注后续还款表现'})
    else:
        factors.append({'name': '最近还款状态', 'risk': 'low', 'detail': '最近月还款正常'})

    # 信用利用率
    util = bill_amt1 / (limit_bal + 1)
    if util > 0.8:
        factors.append({'name': '信用利用率过高', 'risk': 'high',
                        'detail': f'当月账单占额度 {util:.0%}，资金链压力大'})
    elif util > 0.5:
        factors.append({'name': '信用利用率偏高', 'risk': 'medium',
                        'detail': f'当月账单占额度 {util:.0%}，建议关注'})

    # 还款覆盖率
    coverage = pay_amt1 / (bill_amt1 + 1)
    if coverage < 0.3:
        factors.append({'name': '还款覆盖率不足', 'risk': 'high',
                        'detail': f'还款仅覆盖账单的 {coverage:.0%}，存在最低还款行为'})
    elif coverage < 0.7:
        factors.append({'name': '还款覆盖率一般', 'risk': 'medium',
                        'detail': f'还款覆盖账单 {coverage:.0%}'})

    return factors


if __name__ == '__main__':
    main()
