from ultralytics import YOLO

model = YOLO("ball_only/train/weights/best.pt")

results = model.predict(
    source="videos/TT1.mp4",  
    conf=0.25,
    save=True,                       
    project="ball_only",
)
