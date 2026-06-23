# -*- coding: utf-8 -*-
"""
数据集路径检查工具
检查你的图片到底在哪里
"""

import os

print("=" * 60)
print("数据集路径检查工具")
print("=" * 60)

# 检查桌面路径
desktop_path = r'D:\PyCharm Community Edition\102flowers\jpg'
print(f"\n检查桌面路径: {desktop_path}")
print(f"是否存在: {os.path.exists(desktop_path)}")

if os.path.exists(desktop_path):
    print("\n桌面上的文件夹:")
    for item in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item)
        if os.path.isdir(item_path):
            print(f"  📁 {item}")
        else:
            print(f"  📄 {item}")

# 检查others文件夹
others_path = r'D:\Study\dataset\flowers\train'
print(f"\n\n检查others文件夹: {others_path}")
print(f"是否存在: {os.path.exists(others_path)}")

if os.path.exists(others_path):
    print("\nothers文件夹内容:")
    items = os.listdir(others_path)
    print(f"  项目数量: {len(items)}")

    # 检查是否是图片直接在others里
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    direct_images = [f for f in items if os.path.splitext(f)[1].lower() in image_extensions]
    folders = [f for f in items if os.path.isdir(os.path.join(others_path, f))]

    print(f"  直接图片数: {len(direct_images)}")
    print(f"  子文件夹数: {len(folders)}")

    if folders:
        print("\n  子文件夹列表:")
        for folder in folders:
            folder_path = os.path.join(others_path, folder)
            folder_items = os.listdir(folder_path)
            folder_images = [f for f in folder_items if os.path.splitext(f)[1].lower() in image_extensions]
            print(f"    📁 {folder}: {len(folder_images)} 张图片")

            # 显示前5张图片名称
            if folder_images:
                print(f"       示例图片:")
                for img in folder_images[:5]:
                    print(f"         - {img}")

    if direct_images:
        print("\n  ⚠️ 发现图片直接在others文件夹中！")
        print("  这些图片需要按类别放入子文件夹中")
        print("  示例结构:")
        print("    others/")
        print("    ├── class1/")
        print("    │   ├── image1.jpg")
        print("    │   └── image2.jpg")
        print("    └── class2/")
        print("        ├── image1.jpg")
        print("        └── image2.jpg")

print("\n" + "=" * 60)
print("请根据上面的检查结果确认数据集结构")
print("=" * 60)
