# Recruitment Role Data Analytics

岗位数据分析与预测平台 | 深色科技风 Web 应用

## 技术栈
Python + MySQL + Flask + sklearn + ECharts + Playwright

## 项目结构
```
Recruitment Role Data Analytics/
├── config.py                   # 全局配置（数据库/API/路径）
├── utils/                      # 共享工具模块
│   ├── __init__.py             # 福利关键词库（统一维护）
│   └── database.py             # 数据库连接上下文管理器
├── init_database.sql           # 建库建表SQL（含索引）
├── 全国-热门城市岗位数据.csv    # 原始数据（约100条）
├── data_expansion.py           # 数据爬取脚本（Playwright → 51job）
├── data_analysis.py            # 数据分析可视化（8张图表）
├── ml_models.py                # 机器学习建模（3个模型）
├── benefits_crawler.py         # 福利爬虫 + 词云重生成
├── requirements.txt            # Python依赖
├── start_all.bat               # 一键启动脚本
├── static/images/              # 分析图表输出目录
├── models/                     # 训练好的模型文件
└── recruitment_project/        # Flask Web平台
    ├── app.py                  # Flask主程序（API）
    ├── templates/
    │   └── index.html          # 前端页面（HTML结构）
    └── static/
        ├── css/style.css       # 样式表（深色科技风）
        ├── js/app.js           # 前端脚本（ECharts + AI问答）
        └── images/             # 图表文件副本
```

## 数据库
- 数据库：`recruitment_db`
- 表名：`t_recruitment_info`
- 字段：job_name, salary_lower, salary_high, com_name, com_type, com_size, work_year, education, job_benefits, city, district, street
- 数据量：来自51job真实爬取（Playwright浏览器自动化）
- 索引：city, salary_lower, salary_high, com_type, com_size, work_year, education
- **注意**：education/work_year 从标题/标签正则提取（覆盖率有限），com_type/com_size 从公司信息HTML解析，全部为空则留空不编造

## 环境变量（可选，生产环境推荐设置）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | localhost | MySQL 主机 |
| `DB_USER` | root | MySQL 用户 |
| `DB_PASSWORD` | 123456 | MySQL 密码 |
| `DB_NAME` | recruitment_db | 数据库名 |
| `DEEPSEEK_API_KEY` | (内置) | DeepSeek API 密钥 |

```bash
# 设置环境变量示例
set DB_PASSWORD=your_password
set DEEPSEEK_API_KEY=sk-your-key
```

## 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 初始化数据库
```bash
mysql -u root -p < init_database.sql
```

### 3. 一键运行
```bash
start_all.bat
```

### 4. 分步运行
```bash
# Step 1: 数据扩充入库
python data_expansion.py

# Step 2: 数据分析可视化
python data_analysis.py

# Step 3: 机器学习建模
python ml_models.py

# Step 4: 启动Web平台
cd recruitment_project
python app.py
```

访问 http://127.0.0.1:5000

## 功能说明

### 数据看板（8项分析）
1. 城市岗位数量占比（柱状图）
2. 学历要求分布（饼图）
3. 企业类型占比（饼图）
4. 公司岗位排名 TOP15（横向条形图）
5. 工作经验与薪资关系（双轴图）
6. 薪资区间分布（柱状图）
7. 企业规模分布（柱状图）
8. 岗位福利词云

### AI预测（3个模型）
- **决策树**：预测热门城市
- **线性回归**：预测薪资
- **随机森林**：预测招聘强度

### AI 问答
- 基于 DeepSeek 大模型的智能对话
- 支持上下文记忆、多轮对话
- 实时获取数据库统计摘要注入对话

## 注意事项
- 数据分析 (`data_analysis.py`) 和词云生成依赖 Windows 中文字体，Linux/Mac 需修改 `font_path`
- 爬虫脚本依赖 Chrome 浏览器（Playwright 控制）
- 生产环境建议通过环境变量设置数据库密码和 API 密钥
