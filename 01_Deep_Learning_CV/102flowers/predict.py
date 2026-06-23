import os
import random
import torch
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt
from config import Config  # 引入你的配置类

def random_predict():
    config = Config()
    data_root = r'D:\Study\dataset\flowers\test'
    model_path = config.model_save_path
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 获取图片路径
    all_image_paths = []
    for root, dirs, files in os.walk(data_root):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                all_image_paths.append(os.path.join(root, f))
    if not all_image_paths:
        print(f"❌ 错误：在 {data_root} 中没找到图片，请确认是否运行了数据集整理脚本。")
        return
    img_path = random.choice(all_image_paths)
    # 加载模型信息，处理可能的 CPU/GPU 映射问题
    checkpoint = torch.load(model_path, map_location=device)
    class_names = checkpoint['class_names']
    model = models.resnet18()
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device).eval()

    # 预测预处理
    transform = transforms.Compose([
        transforms.Resize((config.image_size, config.image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    img = Image.open(img_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        prob_dist = torch.nn.functional.softmax(output, dim=1)
        prob, pred = torch.max(prob_dist, 1)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.imshow(img)
    plt.title(f"预测类别: {class_names[pred.item()]} \n置信度: {prob.item():.2%}")
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    random_predict()
