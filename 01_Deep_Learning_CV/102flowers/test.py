import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from config import Config
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def test_analysis():
    config = Config()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    transform = transforms.Compose([
        transforms.Resize((config.image_size, config.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_dataset = datasets.ImageFolder(config.test_dir, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    class_names = test_dataset.classes

    # 加载模型
    checkpoint = torch.load(config.model_save_path)
    model = models.resnet18()
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device).eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())


    cm = confusion_matrix(all_labels, all_preds)
    # 1. 显著放大画布
    plt.figure(figsize=(16, 14))
    # 2. 将 annot 设为 False
    sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('混淆矩阵分析图', fontsize=18)
    plt.xlabel('预测值', fontsize=14)
    plt.ylabel('真实值', fontsize=14)
    # 3. 将X轴标签旋转90度，并缩小XY轴的字体
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    # 4. 自动调整布局，防止标签被截断
    plt.tight_layout()
    plt.savefig('混淆矩阵分析图.png', dpi=300) # 增加 dpi 让保存的图片更清晰
    plt.show()


    _, recall, _, _ = precision_recall_fscore_support(all_labels, all_preds, labels=range(len(class_names)))
    # 1. 把画布拉长
    plt.figure(figsize=(20, 6))
    plt.bar(class_names, recall, color='orange')
    plt.title('各类别召回率分析图', fontsize=16)
    plt.ylabel('Recall Score', fontsize=14)
    # 2. X轴标签旋转90度，缩小字体
    plt.xticks(rotation=90, fontsize=8)
    # 3. 自动调整布局
    plt.tight_layout()
    plt.savefig('召回率分析图.png', dpi=300)
    plt.show()

if __name__ == '__main__':
    test_analysis()
