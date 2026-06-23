# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics - 全局配置
安全提示：生产环境请通过环境变量设置 DB_PASSWORD 和 DEEPSEEK_API_KEY
"""
import os
from pathlib import Path

# ============================================================
# 路径
# ============================================================
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "static" / "images"
MODEL_DIR = BASE_DIR / "models"

# ============================================================
# 数据库配置（优先使用环境变量）
# ============================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "db": os.getenv("DB_NAME", "recruitment_db"),
    "charset": "utf8mb4",
}
# data_expansion.py / benefits_crawler.py 使用 "database" 而非 "db"
DB_CONFIG_CRAWLER = {
    "host": DB_CONFIG["host"],
    "user": DB_CONFIG["user"],
    "password": DB_CONFIG["password"],
    "database": DB_CONFIG["db"],
    "charset": "utf8mb4",
}

# ============================================================
# DeepSeek AI 配置
# ============================================================
# 生产环境请通过环境变量或 .env 文件设置 DEEPSEEK_API_KEY
try:
    with open(Path(__file__).parent / ".env") as f:
        for _l in f:
            _l = _l.strip()
            if _l and not _l.startswith("#"):
                _k, _sep, _v = _l.partition("=")
                if _sep:
                    os.environ.setdefault(_k.strip(), _v.strip())
except (OSError, IOError):
    pass
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '') or ''
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# ============================================================
# 机器学习随机种子
# ============================================================
RANDOM_STATE = 42

# ============================================================
# 可视化配色
# ============================================================
COLORS = [
    "#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5",
    "#70AD47", "#264478", "#9B59B6", "#E74C3C", "#1ABC9C",
]
