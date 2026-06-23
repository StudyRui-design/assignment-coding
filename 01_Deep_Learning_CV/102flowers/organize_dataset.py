import os
import shutil
from scipy.io import loadmat
from tqdm import tqdm


def organize_official_dataset():
    # ==================== 路径配置 ====================
    mat_labels = r'D:\Study\imagelabels.mat'
    mat_setid = r'D:\Study\setid.mat'
    source_dir = r'D:\Study\102flowers'
    base_output = r'D:\Study\dataset\flowers'
    # =================================================

    # 1. 加载数据
    labels = loadmat(mat_labels)['labels'][0]
    setid = loadmat(mat_setid)
    # 提取官方定义的 ID
    train_ids = setid['trnid'][0]
    val_ids = setid['valid'][0]
    test_ids = setid['tstid'][0]

    # 2. 建立 ID 到 划分集合的映射
    id_map = {}
    for i in train_ids: id_map[i - 1] = 'train'
    for i in val_ids:   id_map[i - 1] = 'val'
    for i in test_ids:  id_map[i - 1] = 'test'

    # 3. 获取排序后的图片列表
    images = sorted([f for f in os.listdir(source_dir) if f.lower().endswith('.jpg')])
    print("正在按照官方 setid.mat 标准划分数据集...")
    if os.path.exists(base_output):
        shutil.rmtree(base_output)
    for idx, img_name in enumerate(tqdm(images)):
        if idx not in id_map: continue
        # 获取对应的类别和划分归属
        label = labels[idx]
        split_type = id_map[idx]
        # 创建路径
        class_name = f"{label:03d}"
        target_path = os.path.join(base_output, split_type, class_name)
        os.makedirs(target_path, exist_ok=True)
        # 复制文件
        shutil.copy2(os.path.join(source_dir, img_name), os.path.join(target_path, img_name))
    print(f"\n官方标准整理完成！")
    print(f"数据已存储至: {base_output}")


if __name__ == '__main__':
    organize_official_dataset()