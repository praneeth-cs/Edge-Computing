import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

video_path = "video_trimmed.mp4"
cap = cv2.VideoCapture(video_path)

frame_count = 0
frame_gap = 5
prev_gray = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # modulo operation (compare frames further apart)
    if frame_count % frame_gap != 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        continue

    # ----- frame subtraction -----
    diff = cv2.absdiff(gray, prev_gray)

    # ----- contrast stretching -----
    min_val = np.min(diff)
    max_val = np.max(diff)

    if max_val - min_val != 0:
        diff = ((diff - min_val) * (255 / (max_val - min_val))).astype(np.uint8)

    # motion mask
    _, motion_mask = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

    # run YOLO detection
    results = model(frame)[0]

    for box in results.boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label_name = model.names[cls]

        motion_region = motion_mask[y1:y2, x1:x2]

        if motion_region.size == 0:
            continue

        motion_score = np.mean(motion_region)

        # classify static vs dynamic
        if motion_score > 25:
            label = f"{label_name} DYNAMIC"
            color = (0,255,0)
        else:
            label = f"{label_name} STATIC"
            color = (0,0,255)

        cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
        cv2.putText(frame, label, (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Static vs Dynamic Objects", frame)

    prev_gray = gray

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()