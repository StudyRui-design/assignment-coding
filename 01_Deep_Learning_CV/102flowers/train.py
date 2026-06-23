import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import time
import warnings
from config import Config
from charts import run_evaluation

warnings.filterwarnings('ignore')

# 解决绘图时的中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 系统推荐使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def train_model():
    config = Config()

    #  修正训练轮数
    config.num_epochs = 100
    os.makedirs(config.save_dir, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"当前使用的计算设备: {device}")

    #  引入数据增强
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(config.image_size),  # 随机裁剪并缩放
        transforms.RandomHorizontalFlip(),  # 随机水平翻转
        transforms.ToTensor(),
        transforms.Normalize(mean=config.norm_mean, std=config.norm_std)
    ])
    # 测试/验证集：不需要随机性，只做标准的尺寸调整、中心裁剪和归一化
    test_transform = transforms.Compose([
        transforms.Resize((int(config.image_size * 1.14), int(config.image_size * 1.14))),
        transforms.CenterCrop(config.image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=config.norm_mean, std=config.norm_std)
    ])
    # 应用分离的 Transform
    train_dataset = datasets.ImageFolder(config.train_dir, transform=train_transform)
    test_dataset = datasets.ImageFolder(config.test_dir, transform=test_transform)

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    # 加载模型
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, len(train_dataset.classes))
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()

    # 引入 L2 正则化
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=1e-4)
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    best_acc = 0.0

    print("开始训练模型...\n")
    for epoch in range(config.num_epochs):
        epoch_start = time.time()
        # 训练阶段
        model.train()
        train_loss, correct, total = 0, 0, 0
        for imgs, labels in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{config.num_epochs}"):
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            _, pred = outputs.max(1)
            total += labels.size(0)
            correct += pred.eq(labels).sum().item()
        # 验证阶段
        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for imgs, labels in test_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, pred = outputs.max(1)
                val_total += labels.size(0)
                val_correct += pred.eq(labels).sum().item()

        # 记录指标
        acc = 100. * val_correct / val_total
        history['train_loss'].append(train_loss / len(train_loader))
        history['train_acc'].append(100. * correct / total)
        history['val_loss'].append(val_loss / len(test_loader))
        history['val_acc'].append(acc)

        epoch_time = time.time() - epoch_start
        current_lr = optimizer.param_groups[0]['lr']
        tqdm.write(f"Epoch {epoch + 1:3d}/{config.num_epochs} | "
                   f"Time: {epoch_time:5.1f}s | "
                   f"Train Loss: {history['train_loss'][-1]:.4f} | "
                   f"Val Loss: {history['val_loss'][-1]:.4f} | "
                   f"Val Acc: {acc:.2f}% | "
                   f"LR: {current_lr:.2e}")

        # 保存最佳模型
        if acc > best_acc:
            best_acc = acc
            torch.save({'model_state_dict': model.state_dict(), 'class_names': train_dataset.classes},
                       config.model_save_path)
    print("训练完成！正在生成分析图...")

    # 绘图代码
    plt.figure(figsize=(12, 5))
    # 确保横坐标长度与当前已经训练的轮数一致
    current_epoch = len(history['train_loss'])
    epochs_range = range(1, current_epoch + 1)

    # 1. 损失曲线分析图
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, history['train_loss'], label='Train Loss', color='#1f77b4', linewidth=1.5)  # 使用稍暗的蓝色
    plt.plot(epochs_range, history['val_loss'], label='Val Loss', color='#ff7f0e', linewidth=1.5)  # 使用稍暗的橙色
    plt.title(f'损失曲线分析图', fontsize=14)
    plt.xlabel('Epochs')
    plt.legend()
    # 2. 准确率曲线分析图
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, history['train_acc'], label='Train Acc', color='#1f77b4', linewidth=1.5)
    plt.plot(epochs_range, history['val_acc'], label='Val Acc', color='#ff7f0e', linewidth=1.5)
    plt.title(f'准确率曲线分析图', fontsize=14)
    plt.xlabel('Epochs')
    plt.legend(loc='lower right')  # 将准确率图例放到右下角，避免遮挡曲线
    plt.tight_layout()
    # 自动保存分析图
    plt.savefig(os.path.join(config.save_dir, f'analysis_{config.model_name}.png'), dpi=300)
    plt.show()

    # 保存训练历史数据为 JSON，供 Flask Dashboard 的训练曲线使用
    import json
    history_dir = os.path.join(os.path.dirname(__file__), 'evaluation_data')
    os.makedirs(history_dir, exist_ok=True)
    history_path = os.path.join(history_dir, 'history.json')
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"训练历史数据已保存至: {history_path}")

    # 释放训练模型占用的 GPU 显存，准备跑全量测试集评估
    del model
    torch.cuda.empty_cache()

    # 自动运行全量测试集评估，刷新混淆矩阵、per-class 指标等 Dashboard 数据
    print("\n" + "=" * 60)
    print("自动运行测试集评估，生成 Dashboard 数据...")
    print("=" * 60)
    run_evaluation(save=True)
    print("\n所有 Dashboard 数据已更新完毕。")


if __name__ == '__main__':
    train_model()