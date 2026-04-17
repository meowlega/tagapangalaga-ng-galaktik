# 25 epochs should be enough
# CPU because CUDA doesn't work for idk reasons

from ultralytics import YOLO

# Load the Medium model
model = YOLO("yolov8m.pt") 

model.train(
    data="C:/Users/Administrator/Desktop/YOLOAI/Label Studio/data.yaml", # Files are in GDRIVE LINK
    epochs=25,
    imgsz=1280,
    device="cpu",
    batch=16,
    workers=8
)
