from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # load a pretrained model
print("Model loaded. classes:", len(model.names))
