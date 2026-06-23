# 基于 ResNet18 迁移学习的花卉图像分类系统设计与实现

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-PyTorch%20%7C%20Flask-orange.svg)](https://pytorch.org/)
[![Dataset](https://img.shields.io/badge/dataset-Oxford%20102%20Flowers-green.svg)](https://www.robots.ox.ac.uk/~vgg/data/flowers/102/)

本项目为江西科技学院人工智能与大数据学院数据科学与大数据技术专业（23本大数据技术2班）的课程考核项目。项目实现了从数据预处理、深度学习模型训练评估，到最终工程化 Flask Web 可视化系统部署的完整深度学习闭环落地。

## 📌 实验目的
1. **理解残差网络：** 掌握卷积神经网络（CNN）基本原理，深入体会 ResNet 残差网络在图像分类任务中的结构优势。
2. **迁移学习实践：** 使用 ImageNet 预训练的 ResNet18 模型作为特征提取器，通过参数复用缓解小数据集上的过拟合。
3. **闭环流程开发：** 熟练掌握 PyTorch 框架下数据集组织、增强、批量读取、GPU 迭代训练、模型保存与加载的全流程。
4. **细粒度分类评估：** 针对 Oxford 102 Flowers 相似类别的挑战，应用混淆矩阵、逐类精确率、召回率、F1-Score 进行多维技术评估。
5. **工程落地部署：** 利用 Flask 框架搭建后端推理服务，配合 Plotly 交互式图表打造可视化 Web 分析系统。

---

## 📂 数据集准备与预处理

本实验采用经典的 **Oxford 102 Flowers** 数据集，包含 102 种英国常见花卉，共 8189 张 RGB 图像。由于每类样本在 40 至 258 张之间，存在一定的样本不均衡问题。

### 1. 数据集规范化组织
项目利用 `organize_dataset.py` 脚本读取官方 `imagelabels.mat` 与 `setid.mat` 标注文件，将原本扁平存放的图片自动重构为符合 `torchvision.datasets.ImageFolder` 规范的标准树状目录结构：
* **训练集 (Train)：** 约 1,020 张
* **验证集 (Val)：** 约 1,020 张
* **测试集 (Test)：** 约 6,149 张

结构检查确认脚本：`check_dataset.py` 确保目录树处于就绪状态。

### 2. 数据增强与预处理管道
* **训练阶段：** 
  * `RandomResizedCrop(224)` 随机裁剪并缩放至 $224 	imes 224$。
  * `RandomHorizontalFlip(p=0.5)` 随机水平翻转，增强空间泛化性。
* **验证与测试阶段：**
  * `Resize((224, 224))` 固定尺寸缩放，确保稳定、可复现的评估结果。
* **归一化规范：** 转换为 Tensor 后，统一采用 ImageNet 的均值 `[0.485, 0.456, 0.406]` 与标准差 `[0.229, 0.224, 0.225]` 进行通道标准化。
* **批量加载：** 使用 PyTorch `DataLoader` 进行批量高效读取（配置 `batch_size=32`）。

---

## 🧠 模型构建与迁移学习

项目加载 `torchvision.models.resnet18(pretrained=True)` 预训练权重。
1. **骨干网络 (Backbone)：** 包含 1 个初始特征提取层与 4 个残差块层（Layer1-Layer4，包含 2 个 BasicBlock，通道数：64 ➡️ 128 ➡️ 256 ➡️ 512）。
2. **分类头重构 (Classifier Head)：** 将原输出 1000 类的全连接层替换为 `nn.Linear(512, 102)`。
3. **训练策略：** 考虑到细粒度分类的特殊边界，网络卷积层参数（约 11.17M）与新全连接层参数（约 52K）均不冻结，全体参与梯度更新，实现端到端的精细微调（Fine-Tuning）。

### 🛠️ 训练超参数配置
| 配置项 | 取值 | 备注 |
| :--- | :--- | :--- |
| **优化器** | Adam | 具有自适应学习率特性 |
| **初始学习率** | 0.001 | 全程恒定学习率 |
| **权重衰减 (L2 正则化)** | 1e-4 | 抑制参数过拟合 |
| **损失函数** | CrossEntropyLoss | 交叉熵多分类损失 |
| **训练轮数** | 100 Epochs | 耗时约 60 分钟 (CUDA 加速) |
| **批次大小 (Batch Size)** | 32 | 兼顾内存与梯度稳定性 |

---

## 📈 实验结果与多维分析

### 1. 整体性能指标
在含有 **6,149** 张图片的独立测试集上，模型的最优权重取得了 **71.95%** 的整体准确率（正确分类 4424 张，错误 1725 张）。
* **平均召回率 (Avg Recall):** 72.72%
* **平均精确率 (Avg Precision):** 72.45%
* **平均 F1 分数 (Avg F1-Score):** 70.24%

### 2. 类别表现规律
102 类细粒度分类表现呈现一定的分化趋势：
* 召回率 $\ge 90\%$ 的优秀类别共 **18 个**（占 17.65%），其中 `gaura` 和 `silverbush` 两个类别达到了 **100%** 的满分召回率。
* 召回率 $\ge 50\%$ 的稳定类别共 **87 个**（占 85.3%）。
* 召回率 $< 30\%$ 的极难类别仅 **1 个**（占 0.98%），为 `clematis`（铁线莲，26.09%）。

### 3. 典型错误预测案例探讨
针对表现较弱的头部类别，系统通过混淆矩阵和 `visualize.py` 直观捕捉到了系统性误判模式：
* **clematis (082号, 铁线莲 - 召回率 26.1%)：** 极易误判为 `wild pansy`（三色堇），主因两者花瓣色彩梯度与局部轮廓高度近似。
* **sword lily (043号, 剑兰 - 召回率 31.8%)：** 极易误判为 `desert-rose`（沙漠玫瑰），反映出模型对穗状花序整体拓扑特征的捕捉仍有欠缺。
* **sweet pea (004号, 甜豌豆 - 召回率 33.3%)：** 极易与 `ruby-lipped cattleya`（红唇卡特兰）混淆，属于典型的细粒度类间强相似性挑战。

---

## 🖥️ Flask Web 可视化系统部署

为实现深度学习成果的工程落地，本项目基于 Flask 框架搭建了可交互的 Web 演示系统。后端推理模块 (`inference.py`) 采用单例模式，在应用启动时一次性将最优权重加载至 GPU 常驻内存，确保毫秒级实时响应。

系统包含四大核心路由模块：
1. **首页 (`/`)：** 支持单张图片上传。通过模型推理实时计算，返回 Top-1 结果与置信度，并利用图表绘制 Top-5 横向条形分布及 102 类全概率折叠表。
2. **训练曲线页 (`/training`)：** 嵌入 Plotly 生成的交互式损失与准确率收敛曲线，提供测试集性能指标摘要卡。
3. **混淆矩阵页 (`/confusion`)：** 渲染 $102 	imes 102$ 交互式热力图，支持鼠标悬停、局部放大查看误判对，并附带可降序筛选的召回率柱状图。
4. **批量预测页 (`/batch`)：** 随机从验证/测试集中抽取 8 张花卉图像进行并行推理。正确样本以**绿框**标记，错误样本以**红框**突出并并排对比真实与预测标签。

---

## 💡 实验总结与演进方向

### 1. 核心体会
* **迁移学习威力：** 尽管 102 类花卉分类与 ImageNet 的大类有显著差异，但预训练卷积核所具备的底层边缘和纹理特征，让模型在每类仅有约 10 张训练样本的严苛条件下，依然表现出强大的判别边界构建能力。
* **工程闭环的意义：** 深度学习不仅局限于控制台的 Loss 打印。通过将其转化为无编程背景用户也能使用的 Flask 网页，并处理好内存常驻、静态资源路由、安全校验等细节，才是算法走向落地的核心跨越。

### 2. 系统不足与改进思路
* **训练样本被稀释：** 每类可用样本较少导致尾部类别表现不佳。**改进：** 引入 `ColorJitter`、`RandomErasing` 或 `MixUp` 数据增强，或者引入少样本学习 (Few-Shot Learning) 机制。
* **缺乏学习率衰减：** 全程固定 $0.001$ 导致 Epoch 80 后验证损失在平台期高位震荡。**改进：** 引入 `CosineAnnealingLR`（余弦退火）或 `ReduceLROnPlateau` 调度器。
* **细节捕捉能力不足：** ResNet18 的全局平均池化容易丢失局部微小特征。**改进：** 扩展骨干网络至 ResNet50/101，或在残差块间引入 `CBAM`、`SENet` 等注意力机制模块。

---

## 🛠️ 本地运行指南

### 1. 环境准备
```bash
# 克隆仓库
git clone https://github.com/StudyRui-design/assignment-coding.git
cd assignment-coding

# 推荐使用 Conda 搭建 Python 3.11 环境
conda create -n flowers python=3.11 -y
conda activate flowers

# 安装核心依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install flask plotly pandas scipy matplotlib scikit-learn
```

### 2. 执行步骤
* **数据规范整理：** `python organize_dataset.py`
* **启动模型训练：** `python train.py`
* **测试集全面评估：** `python test.py`
* **启动可视化 Web 系统：** `python app.py` (访问本地 `http://127.0.0.1:5000`)