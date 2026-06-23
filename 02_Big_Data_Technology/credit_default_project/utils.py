
# -*- coding: utf-8 -*-
"""
utils.py — 工具函数模块
信用卡违约预测项目 | 数据挖掘实验期末考核
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互后端，支持无GUI环境生成图表
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from matplotlib import rcParams

# ============================
# 全局绘图风格配置（健壮的中文字体配置）
# ============================

def _register_cjk_fonts():
    """向 fontManager 注册中文字体文件（在 sns 设置之前调用）"""
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
        'SimHei', 'Microsoft YaHei', 'STXihei',       # Windows
        'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',    # Linux
        'Noto Sans CJK SC', 'Noto Sans SC',             # Linux (通用)
        'PingFang SC', 'Heiti SC', 'STHeiti',           # macOS
        'Arial Unicode MS',                              # 跨平台回退
    ]
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    for font_name in _CJK_FONT_CANDIDATES:
        if font_name in available_fonts:
            rcParams['font.sans-serif'] = [font_name] + \
                [f for f in rcParams['font.sans-serif'] if f != font_name]
            rcParams['font.family'] = 'sans-serif'
            rcParams['axes.unicode_minus'] = False
            return
    rcParams['font.family'] = 'sans-serif'
    rcParams['axes.unicode_minus'] = False
    print("[警告] 未找到中文字体，图表中文可能无法正常显示", file=sys.stderr)


# 第一步：注册字体文件
_register_cjk_fonts()

# 第二步：设置 seaborn 风格（会重置部分 rcParams）
sns.set_style("whitegrid")
sns.set_palette("Set2")

# 第三步：在 sns 之后覆盖字体设置（关键！）
_setup_chinese_font()

rcParams['figure.dpi'] = 150
rcParams['savefig.dpi'] = 150
rcParams['savefig.bbox'] = 'tight'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, 'figures')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
DATA_PATH = os.path.join(BASE_DIR, 'data.csv')

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data(path=DATA_PATH):
    """加载原始数据集"""
    return pd.read_csv(path)


def save_fig(fig, name):
    """保存图表到 figures 目录"""
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f'[图] 已保存: {path}')


def save_model(model, name):
    """保存模型到 models 目录"""
    path = os.path.join(MODEL_DIR, name)
    joblib.dump(model, path)
    print(f'[模型] 已保存: {path}')


def load_model(name):
    """从 models 目录加载模型"""
    path = os.path.join(MODEL_DIR, name)
    return joblib.load(path)
