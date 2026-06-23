# -*- coding: utf-8 -*-
"""
第一步：检测环境是否正确安装
在PyCharm中运行此文件
"""

import sys

print("=" * 60)
print("环境检测")
print("=" * 60)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print()

# 检测 PyTorch
try:
    import torch

    print("✓ PyTorch 已安装")
    print(f"  版本: {torch.__version__}")

    # 检测 CUDA
    if torch.cuda.is_available():
        print("✓ CUDA 可用")
        print(f"  CUDA版本: {torch.version.cuda}")
        print(f"  GPU设备: {torch.cuda.get_device_name(0)}")
        print(f"  GPU数量: {torch.cuda.device_count()}")
    else:
        print("✗ CUDA 不可用（将使用CPU训练，速度较慢）")

except ImportError:
    print("✗ PyTorch 未安装")
    print("\n请在PyCharm终端运行以下命令安装：")
    print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

print()

# 检测 torchvision
try:
    import torchvision

    print("✓ TorchVision 已安装")
    print(f"  版本: {torchvision.__version__}")
except ImportError:
    print("✗ TorchVision 未安装")

print()

# 检测其他依赖
dependencies = ['matplotlib', 'seaborn', 'sklearn', 'numpy', 'tqdm']
for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep} 已安装")
    except ImportError:
        print(f"✗ {dep} 未安装")

print()
print("=" * 60)

# 检测数据集路径
import os

dataset_path = r'D:\Study\dataset\flowers\train'
print(f"\n数据集路径检测:")
print(f"  路径: {dataset_path}")
print(f"  是否存在: {os.path.exists(dataset_path)}")

if os.path.exists(dataset_path):
    # 查看文件夹内容
    items = os.listdir(dataset_path)
    folders = [item for item in items if os.path.isdir(os.path.join(dataset_path, item))]
    print(f"  文件夹数量: {len(folders)}")
    print(f"  文件夹列表:")
    for i, folder in enumerate(folders[:10], 1):  # 只显示前10个
        folder_path = os.path.join(dataset_path, folder)
        num_files = len([f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
        print(f"    {i}. {folder} ({num_files} 张图片)")
    if len(folders) > 10:
        print(f"    ... 还有 {len(folders) - 10} 个文件夹")

print()
print("=" * 60)
print("如果所有检测项都显示 ✓，可以继续下一步！")
print("如果有 ✗，请先安装对应的包")
print("=" * 60)
