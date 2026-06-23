import torch
import matplotlib.pyplot as plt
import numpy as np
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from config import Config
import warnings

warnings.filterwarnings('ignore')

# 解决绘图时的中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def visualize_validation_batch():
    config = Config()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"当前使用的计算设备: {device}")

    # 1. 定义验证集的数据预处理
    val_transform = transforms.Compose([
        transforms.Resize((int(config.image_size * 1.14), int(config.image_size * 1.14))),
        transforms.CenterCrop(config.image_size),
        transforms.ToTensor(),
        # 使用 ImageNet 标准均值和方差
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 2. 加载验证集
    val_dataset = datasets.ImageFolder(config.test_dir, transform=val_transform)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=True)

    checkpoint = torch.load(config.model_save_path, map_location=device)
    class_names = checkpoint.get('class_names', val_dataset.classes)

    # 3. 加载训练好的模型
    model = models.resnet18()
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device).eval()

    # 4. 随机获取一个批次的数据
    dataiter = iter(val_loader)
    images, labels = next(dataiter)
    images_cuda = images.to(device)

    # 5. 进行模型预测
    with torch.no_grad():
        outputs = model(images_cuda)
        prob_dist = torch.nn.functional.softmax(outputs, dim=1)
        probs, preds = torch.max(prob_dist, 1)

    # 6. 开始画图：展示 2行 x 4列 的图像网格
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle('验证集抽样预测分析 (真实标签 vs 预测标签)', fontsize=20, fontweight='bold')

    for idx in range(8):
        if idx >= len(images): break

        ax = fig.add_subplot(2, 4, idx + 1, xticks=[], yticks=[])

        # 反归一化：将 Tensor 转换回正常的 RGB 图片格式才能在 matplotlib 显示
        img = images[idx].numpy().transpose((1, 2, 0))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = std * img + mean
        img = np.clip(img, 0, 1)  # 限制 RGB 值在 0~1 之间

        plt.imshow(img)

        true_label = class_names[labels[idx].item()]
        pred_label = class_names[preds[idx].item()]
        confidence = probs[idx].item()

        # 预测正确显示绿色，错误显示红色
        color = 'green' if true_label == pred_label else 'red'

        title_text = f'真实: {true_label}\n预测: {pred_label} ({confidence:.1%})'
        ax.set_title(title_text, color=color, fontsize=13)

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)  # 给总标题留出空间
    plt.show()


if __name__ == '__main__':
    visualize_validation_batch()