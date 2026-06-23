from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('yolo11n.pt')
    # 添加 device=0 指定使用第0块GPU
    results = model.train(
        data='coco128.yaml',
        epochs=100,
        imgsz=640,
        workers=0,
        device=0  # ← 关键：指定GPU
    )
