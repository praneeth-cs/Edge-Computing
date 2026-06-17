import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

video_path = "video_trimmed.mp4"
cap = cv2.VideoCapture(video_path)

vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

frame_count = 0
frame_gap = 5
prev_gray = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # modulo frame skipping
    if frame_count % frame_gap != 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        continue

    # frame subtraction
    diff = cv2.absdiff(gray, prev_gray)

    # contrast stretching
    min_val = np.min(diff)
    max_val = np.max(diff)

    if max_val - min_val != 0:
        diff = ((diff - min_val) * (255 / (max_val - min_val))).astype(np.uint8)

    # motion threshold
    _, motion_mask = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

    # run YOLO detection
    results = model(frame)[0]

    output = np.zeros_like(frame)  # black background

    for box in results.boxes:
        cls = int(box.cls[0])

        if cls not in vehicle_classes:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # check if motion exists inside bounding box
        motion_region = motion_mask[y1:y2, x1:x2]

        if np.mean(motion_region) > 20:  # moving vehicle threshold
            output[y1:y2, x1:x2] = frame[y1:y2, x1:x2]

    cv2.imshow("Moving Vehicles Only", output)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()