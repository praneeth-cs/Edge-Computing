import cv2
import os
import requests
import numpy as np
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
CLOUD_IP = "172.20.10.3"
UPLOAD_URL = f"http://{CLOUD_IP}:5000/upload"

FPS = 30
DURATION = 10
TOTAL_FRAMES = FPS * DURATION

LOW_THRESHOLD = 1      # %
HIGH_THRESHOLD = 80    # %

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_ID = f"run_{timestamp}"
FRAMES_FOLDER = f"frames_{timestamp}"

os.makedirs(FRAMES_FOLDER, exist_ok=True)

# -----------------------------
# STEP 1: RECORD VIDEO
# -----------------------------
print("Recording video at EDGE...")

cap_cam = cv2.VideoCapture(0)

frame_width = int(cap_cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_name = f"output_{timestamp}.mp4"
out = cv2.VideoWriter(video_name, fourcc, FPS, (frame_width, frame_height))

frames = []

count = 0
while count < TOTAL_FRAMES:
    ret, frame = cap_cam.read()
    if not ret:
        break

    out.write(frame)
    frames.append(frame)
    count += 1

cap_cam.release()
out.release()

print("Video recorded.")

# -----------------------------
# STEP 2: EDGE PROCESSING + DECISION
# -----------------------------
print("Edge processing started...")

previous_gray = None

for i, frame in enumerate(frames):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if previous_gray is None:
        # First frame → always keyframe
        frame_type = "keyframe"
        send_image = frame
        diff_percent = 100.0
    else:
        diff = cv2.absdiff(gray, previous_gray)
        changed_pixels = np.count_nonzero(diff)
        total_pixels = diff.size

        diff_percent = (changed_pixels / total_pixels) * 100

        if diff_percent < LOW_THRESHOLD:
            print(f"Frame {i+1}: {diff_percent:.2f}% → NOT sent")
            previous_gray = gray
            continue

        elif diff_percent >= HIGH_THRESHOLD:
            frame_type = "keyframe"
            send_image = frame

        else:
            frame_type = "delta"
            send_image = cv2.absdiff(frame, frames[i-1])

    # -----------------------------
    # SAVE LOCALLY
    # -----------------------------
    filename = f"{frame_type}_{i+1:03d}.jpg"
    local_path = os.path.join(FRAMES_FOLDER, filename)
    cv2.imwrite(local_path, send_image)

    # -----------------------------
    # SEND TO CLOUD
    # -----------------------------
    with open(local_path, 'rb') as f:
        files = {'frame': (filename, f)}
        data = {
            'run_id': RUN_ID,
            'frame_type': frame_type,
            'diff_percent': f"{diff_percent:.2f}"
        }
        response = requests.post(UPLOAD_URL, files=files, data=data)

    print(
        f"Frame {i+1}: {diff_percent:.2f}% → SENT ({frame_type})"
    )

    previous_gray = gray

print("Edge processing + transmission complete.")
