from ultralytics import YOLO


if __name__ == '__main__':
    # Create a new YOLO model from scratch
    model = YOLO("yolo11s.yaml")

    results = model.train(data="data.yaml", epochs=20, device=0)

    # Evaluate the model's performance on the validation set
    results = model.val()

    # Export the model to ONNX format
    model.export()

#건들지 마세요 사나워요 물어요


