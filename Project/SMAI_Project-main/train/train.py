from ultralytics import YOLO


model = YOLO("yolov8n.pt")  

# Please change the path in yaml file according to images path of test train and val.

model.train(
    data="ttnet_ball.yaml",     
    epochs=20,                  
    imgsz=320,
    batch=16,
    project="ball_only",   
)
