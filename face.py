# save this as capture_images.py

import cv2, os, time, argparse

def capture_images(output_dir, count=100, delay=1.0, cam_index=0):
    """
    Capture `count` frames from webcam `cam_index`, 
    saving one image every `delay` seconds into `output_dir`.
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {cam_index}")

    print(f"Starting capture: {count} images → {output_dir}")
    for i in range(count):
        ret, frame = cap.read()
        if not ret:
            print("  ✗ Frame grab failed, stopping.")
            break
        timestamp = int(time.time()*1000)
        fname = os.path.join(output_dir, f"img_{timestamp}_{i:03d}.jpg")
        cv2.imwrite(fname, frame)
        print(f"  ✓ Saved {fname}")
        time.sleep(delay)

    cap.release()
    print("Capture complete.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Batch-capture webcam images into a folder"
    )
    p.add_argument("output_dir", help="Where to save images")
    p.add_argument("--count", type=int, default=100, help="Number of pics")
    p.add_argument("--delay", type=float, default=1.0,
                   help="Seconds between captures")
    p.add_argument("--cam", type=int, default=0,
                   help="OpenCV camera index (0,1,...)")
    args = p.parse_args()

    capture_images(args.output_dir, args.count, args.delay, args.cam)
