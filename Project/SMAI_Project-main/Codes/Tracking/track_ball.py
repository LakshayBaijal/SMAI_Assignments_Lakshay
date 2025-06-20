import cv2
import numpy as np
from ultralytics import YOLO


class KalmanBallTracker:
    def __init__(self):
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1,0,0,0],
                                              [0,1,0,0]], np.float32)
        dt = 1.0
        self.kf.transitionMatrix = np.array([[1,0,dt,0],
                                             [0,1,0,dt],
                                             [0,0,1,0],
                                             [0,0,0,1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-2
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-1

        self.initialized = False

    def predict(self):
        x = self.kf.predict()
        return x[0], x[1]

    def update(self, meas):
        """ meas = (x, y) """
        m = np.array([[np.float32(meas[0])],
                      [np.float32(meas[1])]])
        if not self.initialized:
            self.kf.statePost = np.array([[m[0,0]],
                                           [m[1,0]],
                                           [0],
                                           [0]], np.float32)
            self.initialized = True
        return self.kf.correct(m)[:2].flatten()



model = YOLO('ball_only/train/weights/best.pt') 
cap   = cv2.VideoCapture('videos/TT2.mp4')
w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps   = cap.get(cv2.CAP_PROP_FPS)


fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out    = cv2.VideoWriter('track_out.mp4', fourcc, fps, (w, h))

tracker = KalmanBallTracker()

while True:
    ret, frame = cap.read()
    if not ret: break

    results = model(frame, conf=0.15, imgsz=320)[0] 

    if len(results.boxes) > 0:
        best = results.boxes.conf.argmax()
        x1,y1,x2,y2 = results.boxes.xyxy[best].cpu().numpy()
        cx, cy     = (x1+x2)/2, (y1+y2)/2
        px, py     = tracker.update((cx, cy))
        color      = (0,255,0)  
    else:
        px, py = tracker.predict()
        color   = (0,0,255)      


    cv2.circle(frame, (int(px), int(py)), 8, color, -1)
    out.write(frame)

    cv2.imshow('ball track', frame)
    if cv2.waitKey(1) == 27: 
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print("✔️ Done – saved to track_out.mp4")
