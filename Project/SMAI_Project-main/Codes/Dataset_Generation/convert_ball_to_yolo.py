#!/usr/bin/env python3
"""
convert_ball_to_yolo.py

Convert TTNet JSON annotations into YOLO-format
labels for train/val/test splits, prefixing filenames with 'img_' to match frame images.
"""
import os
import json
from glob import glob

# configuration
BOX_HALF = 16       # half-size of the ball bounding box in pixels
W, H = 1920, 1080    # full frame width/height

# splits mapping
splits = {
    'game_1':'train','game_2':'train','game_3':'train','game_4':'train','game_5':'val',
    'test_1':'test','test_2':'test','test_3':'test','test_4':'test','test_5':'test','test_6':'test','test_7':'test'
}

DATASET_ROOT = 'dataset'
YOLO_LABEL_ROOT = os.path.join('yolo_dataset', 'labels')

# ensure label dirs exist
for split in set(splits.values()):
    os.makedirs(os.path.join(YOLO_LABEL_ROOT, split), exist_ok=True)

# process ball annotations (class 0)
for name, split in splits.items():
    ann_path = os.path.join(DATASET_ROOT,
                            'training' if name.startswith('game_') else 'test',
                            'annotations', name, 'ball_markup.json')
    if not os.path.isfile(ann_path):
        print(f"Skipping missing annotation: {ann_path}")
        continue
    data = json.load(open(ann_path))
    out_dir = os.path.join(YOLO_LABEL_ROOT, split)

    for fid_str, coord in data.items():
        try:
            fid = int(fid_str)
            x, y = coord['x'], coord['y']
        except:
            continue
        if x < 0 or y < 0:
            continue
        # compute box corners
        x0 = max(0, x - BOX_HALF)
        y0 = max(0, y - BOX_HALF)
        x1 = min(W, x + BOX_HALF)
        y1 = min(H, y + BOX_HALF)
        # normalize to YOLO format
        xc = ((x0 + x1) / 2) / W
        yc = ((y0 + y1) / 2) / H
        wb = (x1 - x0) / W
        hb = (y1 - y0) / H
        # label filename prefixing 'img_'
        lbl_fn = f"img_{fid:06d}.txt"
        lbl_path = os.path.join(out_dir, lbl_fn)
        with open(lbl_path, 'w') as f:
            f.write(f"0 {xc:.6f} {yc:.6f} {wb:.6f} {hb:.6f}\n")

print("YOLO ball-only labels generated with 'img_' prefix.")