# -*- coding: utf-8 -*-
import os
import torch


class Config:
    """
    实验配置文件 - 针对花卉识别项目优化
    """
    # ==================== 1. 数据集路径 ====================
    # 项目根目录（自动推导，无需修改）
    _project_root = os.path.dirname(os.path.abspath(__file__))
    # 划分后的数据集存放路径
    root_dir = os.path.join(_project_root, 'data', 'dataset')
    train_dir = os.path.join(root_dir, 'train')
    test_dir = os.path.join(root_dir, 'test')

    # ==================== 2. 模型超参数 ====================
    # 模型为 resnet50
    model_name = 'resnet50'
    # 100 轮以获得更平滑的 Loss 曲线
    num_epochs = 100
    # 显存充足建议 32，若显存溢出(OOM)可降为 16 或 8
    batch_size = 32
    learning_rate = 0.001

    # ==================== 3. 图像预处理参数 ====================
    image_size = 224  # ResNet 系列标准输入
    # ImageNet 数据集的均值和标准差
    norm_mean = [0.485, 0.456, 0.406]
    norm_std = [0.229, 0.224, 0.225]

    # ==================== 4. 硬件与保存配置 ====================
    # 自动识别计算设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Windows系统下必须为 0，防止多线程死锁
    num_workers = 0

    # 结果保存路径
    save_dir = os.path.join(_project_root, 'results')

    def __init__(self):
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    @property
    def model_save_path(self):
        """动态生成模型保存路径"""
        return os.path.join(self.save_dir, f'{self.model_name}_best.pth')

    @property
    def plot_save_path(self):
        """动态生成 Loss 曲线图保存路径"""
        return os.path.join(self.save_dir, f'loss_curve_{self.model_name}.png')


# 实例化配置对象供 train.py 使用
config = Config()