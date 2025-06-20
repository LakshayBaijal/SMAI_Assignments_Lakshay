import cv2
import os
import math

video_path = "videos/TT2.mp4"
label_folder = "runs/detect/predict2/labels"
output_path = "output_arrow_fixed.mp4"

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

prev_center = None
prev_speed = 0
prev_angle = 0

for frame_idx in range(frame_count):
    ret, frame = cap.read()
    if not ret:
        break

    label_file = os.path.join(label_folder, f"TT2_{frame_idx}.txt")
    if os.path.exists(label_file):
        with open(label_file, 'r') as f:
            lines = f.readlines()

        if lines:
            parts = lines[0].strip().split()
            if len(parts) == 5:
                cls, x_center, y_center, w, h = map(float, parts)
                x_pixel = int(x_center * width)
                y_pixel = int(y_center * height)

                cv2.circle(frame, (x_pixel, y_pixel), 5, (255, 0, 0), -1)

                if prev_center:
                    dx = x_pixel - prev_center[0]
                    dy = y_pixel - prev_center[1]
                    speed = math.sqrt(dx**2 + dy**2)
                    angle = math.degrees(math.atan2(dy, dx)) % 360

                    arrow_scale = 2
                    end_point = (int(prev_center[0] + dx * arrow_scale), int(prev_center[1] + dy * arrow_scale))
                    cv2.arrowedLine(frame, prev_center, end_point, (0, 255, 255), 2, tipLength=0.3)

                    prev_speed = speed
                    prev_angle = angle

                prev_center = (x_pixel, y_pixel)

    if prev_center:
        cv2.putText(frame, f"Speed: {prev_speed:.2f}px/frame", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Angle: {prev_angle:.2f}°", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    out.write(frame)

cap.release()
out.release()
print("✅ Output saved as:", output_path)
