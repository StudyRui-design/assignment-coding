# 📚 Study Portfolio — 课程项目统一代码库

> 研究生阶段课程作业与实践项目的集中归档仓库，涵盖深度学习计算机视觉、大数据技术、数据分析等方向。

[![GitHub last commit](https://img.shields.io/github/last-commit/StudyRui-design/assignment-coding)](https://github.com/StudyRui-design/assignment-coding)

---

## 📁 仓库结构

```
.
├── 01_Deep_Learning_CV/          ← 计算机视觉 & 深度学习
│   ├── 102flowers/               # ResNet18 迁移学习花卉分类系统
│   ├── Semantic_Segmentation/    # 语义分割项目
│   └── YOLO_Projects/            # YOLO 目标检测（v8 / v11 / v26）
│
├── 02_Big_Data_Technology/       ← 大数据技术 & 数据分析
│   ├── Movie_Analysis/           # 电影推荐与 Spark 数据分析
│   ├── Recruitment_Role_Data_Analytics/  # 招聘岗位数据采集与分析平台
│   ├── credit_default_project/   # 信用违约预测（EDA → 建模 → Web 部署）
│   └── market-pulse/             # 市场脉搏数据看板（前后端分离）
│
└── 03_Projects/                  ← 综合实训 & 工具代码
    ├── IELTS_Practice_Project/   # 雅思练习平台（SpringBoot + Flask + Spark）
    └── code/                     # PySpark 实训、鸢尾花分类等小实验
```

---

## 🧠 01 — 深度学习 & 计算机视觉

### 🌸 102flowers — 花卉图像分类系统

基于 **ResNet18 迁移学习**的 102 类花卉细粒度分类 Web 应用。

| 维度 | 详情 |
|------|------|
| **框架** | PyTorch + Flask |
| **模型** | ResNet18 (ImageNet 预训练 → 微调) |
| **数据集** | [Oxford 102 Flowers](https://www.robots.ox.ac.uk/~vgg/data/flowers/102/) |
| **功能** | 单张 / 批量推理、混淆矩阵、Top-K 准确率、训练曲线可视化 |
| **入口** | `app.py` — Flask 启动入口；`train.py` — 训练脚本 |

### 🎯 YOLO Projects — 目标检测实验

YOLO 系列模型的训练与推理实验，覆盖多个版本对比。

| 文件 | 说明 |
|------|------|
| `train.py` | YOLO 训练脚本 |
| `yolov8n.pt` | YOLOv8 Nano 预训练权重 |
| `yolo11n.pt` | YOLOv11 Nano 预训练权重 |
| `yolo26n.pt` | YOLOv26 Nano 预训练权重 |

### 🧩 Semantic Segmentation

语义分割相关实验项目。

---

## 📊 02 — 大数据技术 & 数据分析

### 💳 Credit Default Project — 信用违约预测

完整的机器学习流水线：从探索性分析到 Web 部署。

| 阶段 | 脚本 | 说明 |
|------|------|------|
| 1️⃣ EDA | `1_eda.py` | 探索性数据分析 |
| 2️⃣ 预处理 | `2_preprocessing.py` | 数据清洗与特征工程 |
| 3️⃣ 建模 | `3_modeling.py` | 模型训练与对比 |
| 4️⃣ 调优 | `4_tuning.py` | 超参数搜索 |
| 5️⃣ 部署 | `5_app.py` | 模型 Web 服务 |

### 🎬 Movie Analysis — 电影数据分析

基于 **Apache Spark** 的电影评分与推荐分析。

- **数据源**：MovieLens 1M 数据集
- **技术栈**：PySpark + Flask
- `spark_analysis/` — Spark 分析脚本
- `preprocess_data.py` — 数据预处理
- `app.py` — 可视化展示

### 💼 Recruitment Role Data Analytics — 招聘数据分析

岗位数据多源采集、清洗与机器学习分析平台。

- **架构**：Flask + 多源爬虫 + ML 模型
- **数据**：全国热门城市岗位数据
- **功能**：数据采集 → 清洗 → 特征分析 → 可视化

### 📈 Market Pulse — 市场脉搏

前后端分离的市场数据看板应用。

```
market-pulse/
├── backend/    # 后端 API 服务
└── frontend/   # 前端可视化界面
```

---

## 🛠 03 — 综合项目 & 工具

### 📖 IELTS Practice Project — 雅思练习平台

企业级微服务架构的雅思学习系统。

| 模块 | 技术栈 |
|------|--------|
| `sft-springboot/` | SpringBoot 主服务 |
| `flask-service/` | Flask 算法服务 |
| `spark-service/` | Spark 数据处理 |
| `sql/` | 数据库设计脚本 |

### 🧪 code — 实验代码

- `Pyspark/` — PySpark 大数据实训项目
- `iris/` — 鸢尾花经典分类实验
- `大数据技术开发实训/` — 课程实训资料

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/StudyRui-design/assignment-coding.git
cd assignment-coding

# 安装 Python 依赖（以 102flowers 为例）
cd 01_Deep_Learning_CV/102flowers
pip install -r requirements.txt
python app.py
```

---

## 🛠 技术栈总览

| 领域 | 技术 |
|------|------|
| **深度学习** | PyTorch, torchvision, ResNet18, YOLOv8/v11 |
| **大数据** | Apache Spark, PySpark, Hadoop |
| **后端** | Flask, SpringBoot |
| **前端** | HTML/CSS/JS, Bootstrap, ECharts |
| **数据处理** | Pandas, NumPy, Matplotlib |
| **ML** | Scikit-learn, XGBoost, LightGBM |

---

## ⚠️ 注意事项

- **模型权重**（`.pth`、`.pkl`）和**大型数据集**（`data/raw/`、`data/dataset/`）已加入 `.gitignore`，不会随仓库推送，请按项目文档自行下载或训练。
- 各子项目内的 `README.md` 包含更详细的使用说明和环境配置。
- Python 版本建议 ≥ 3.10。

---

*Last updated: 2026-06-23*
