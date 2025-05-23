import time
import cv2
from datetime import datetime

RTSP_URL = "rtsp://video-relay:8554/mystream"


for i in range(30):
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if cap.isOpened():
        print(f"[INFO] Connected to stream on attempt {i + 1}")
        break
    print(f"[WARN] Stream not available, retrying ({i + 1})...")
    time.sleep(1)


if not cap.isOpened():
    raise Exception("Failed to open RTSP stream")

print("RTSP stream opened successfully.")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame.")
        break

    frame_count += 1
    print(
        f"Frame #{frame_count}: {frame.shape} @:{datetime.now().isoformat()}", flush=True)

cap.release()
