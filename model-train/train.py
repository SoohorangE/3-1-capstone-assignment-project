from ultralytics import YOLO

if __name__ == '__main__':
    # Load a pretrained YOLOv8s model
    model = YOLO("yolov8s.pt")

    print(f"Loaded model type: {model.model_name}")
    print(f"Loaded model yaml: {model.yaml_file}")

    results = model.train(data="data.yaml", epochs=20, imgsz=1024, device="cuda", batch=8)

    # Evaluate the model's performance on the validation set
    results = model.val()

    # Export the model
    model.export()
