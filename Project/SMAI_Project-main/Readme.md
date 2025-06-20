## SMAI Project

### Youtube Implementation Video

```bash
https://www.youtube.com/watch?v=s2lVYqKBQPE
```

### Ball Tracking Results.

https://github.com/user-attachments/assets/f7501964-5db0-43c4-8fa5-f4a58084c32e

https://github.com/user-attachments/assets/a6eb28c6-14dd-4069-aa4a-199b15a84319



## 📁 Dataset and Preprocessing

- **Dataset**: TTNet dataset, which provides JSON-based annotations for table tennis ball positions in each frame.
- **Focus**: Only the **ball** is detected (no table or player detection).


## 📁 Directory Structure:
    ```
    yolo_dataset/
    ├── images/
    │   ├── train/
    │   └── val/
    └── labels/
    │   ├── train/
    │   └── val/
    ├── ball_analysis.py
    ├── classes.txt
    ├── track_ball.py
    ├── ttnet_ball.yaml
    ├── yolov8n.pt
    ├── Dataset_Generation/
        ├── download_dataset.py
        ├── extract_all_images.py
        └── extract_selected_images.py
    └── convert_ball_to_yolo.py
    
    ```

---

## ⚙️ Model Training

- **Model Used**: `yolov8n.pt` (Nano version for faster training).
- **Training Command**:
  ```bash
  yolo train model=yolov8n.pt data=ttnet_ball.yaml epochs=20 imgsz=640 batch=16 project=TTBallProject name=ball_yolo_model
  ```

## 🔍 Inference
- **Command**:
  ```bash
  yolo predict model=TTBallProject/ball_yolo_model/weights/best.pt source=videos/TT1.mp4 conf=0.25 save=True
  ```

- This generates an annotated output video with bounding boxes around detected balls.

## 📈 Post-Processing: Speed & Direction
- A script (post_process_speed_angle.py) was implemented to:

- Read YOLO predictions from .txt files.

- Calculate speed using Euclidean distance between detected centers in consecutive frames.

- Compute direction using arctangent (atan2) function.

- Annotate video with speed (px/frame) and angle (degrees).

- Distance: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
- Speed: speed = d / time_between_frames
- Direction - angle = atan2(y2 - y1, x2 - x1) × (180 / π)
- Final Output: Annotated video with bounding boxes, speed, and direction arrow.

## 📌 Notes

- Trained entirely locally due to GPU session limits in Kaggle.

- Focused only on ball tracking.

- Could be extended to detect bounce events, estimate speed in m/s, or predict ball trajectory.

## 📎 Links
- Dataset Sample (Converted to YOLO format)
  ```bash
  https://www.kaggle.com/datasets/svmohitkumar/smai-project-dataset
  ```
- Video on Implementation of Ball Tracking (Voice Reveal Here)
  ```bash
  https://www.youtube.com/watch?v=s2lVYqKBQPE
  ```
- Reports about this Project
  ```bash
  https://github.com/LakshayBaijal/SMAI_Project/tree/main/Submissions
  ``` 
