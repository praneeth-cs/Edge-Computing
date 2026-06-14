import cv2
import os
import requests
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
CLOUD_IP = "192.168.0.246"
UPLOAD_URL = f"http://{CLOUD_IP}:5000/upload"


FPS = 30
DURATION = 10
TOTAL_FRAMES = FPS * DURATION

# unique folder name using timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
VIDEO_NAME = f"output_{timestamp}.mp4"
FRAMES_FOLDER = f"frames_{timestamp}"

# -----------------------------
# STEP 1: RECORD VIDEO
# -----------------------------
print("STEP 1: Recording video...")

camera = cv2.VideoCapture(0)

frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(VIDEO_NAME, fourcc, FPS, (frame_width, frame_height))

count = 0
while count < TOTAL_FRAMES:
    ret, frame = camera.read()
    if not ret:
        break

    out.write(frame)
    cv2.imshow("EDGE Recording", frame)
    count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
out.release()
cv2.destroyAllWindows()

print("Video recording completed.")

# -----------------------------
# STEP 2: EXTRACT FRAMES
# -----------------------------
print("STEP 2: Extracting frames...")

os.makedirs(FRAMES_FOLDER, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_NAME)
frame_id = 0

while frame_id < TOTAL_FRAMES:
    ret, frame = cap.read()
    if not ret:
        break

    frame_path = os.path.join(
        FRAMES_FOLDER, f"frame_{frame_id+1:03d}.jpg"
    )
    cv2.imwrite(frame_path, frame)
    frame_id += 1

cap.release()

print(f"{frame_id} frames saved in folder: {FRAMES_FOLDER}")

# -----------------------------
# STEP 3: SEND FRAMES TO CLOUD
# -----------------------------
print("STEP 3: Sending frames to cloud...")

run_id = FRAMES_FOLDER  # use timestamp-based folder name

for filename in sorted(os.listdir(FRAMES_FOLDER)):
    file_path = os.path.join(FRAMES_FOLDER, filename)

    with open(file_path, 'rb') as f:
        files = {'frame': (filename, f)}
        data = {'run_id': run_id}
        response = requests.post(UPLOAD_URL, files=files, data=data)

    print(f"Sent {filename} | Status {response.status_code}")
