import cv2
import time
from datetime import datetime
import os

RTSP_URL = "rtsp://video-relay:8554/mystream"
OUTPUT_BASE_DIR = "/app/frames"


for i in range(30):
    cap = cv2.VideoCapture(RTSP_URL)
    if cap.isOpened():
        print(f"[INFO] Connected to stream on attempt {i + 1}")
        break
    print(f"[WARN] Stream not available, retrying ({i + 1})...")
    time.sleep(1)


if not cap.isOpened():
    raise IOError("Failed to open RTSP stream")

print("RTSP stream opened successfully.")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame.")
        break

    frame_count += 1
    now = datetime.now()
    date_folder = now.strftime("%Y_%m_%d")
    timestamp = now.strftime("%H%M%S_%f")

    output_dir = os.path.join(OUTPUT_BASE_DIR, date_folder)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"frame_{frame_count}_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    cv2.imwrite(filepath, frame)

    print(f"[SAVED] {filepath} | Shape: {frame.shape}", flush=True)


cap.release()
