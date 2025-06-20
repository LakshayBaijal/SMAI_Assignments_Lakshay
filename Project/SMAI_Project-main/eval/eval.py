from ultralytics import YOLO

# Load trained model
model = YOLO("ball_only/train/weights/best.pt")

# Evaluate performance on validation set
metrics = model.val()
print(metrics)
