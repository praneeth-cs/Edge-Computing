import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict, deque

model = YOLO("yolov8n.pt")

video_path = "video_trimmed.mp4"
cap = cv2.VideoCapture(video_path)

frame_count = 0
frame_gap = 5
prev_gray = None
prev_boxes = []

# history buffer
history = defaultdict(lambda: deque(maxlen=5))

def compute_iou(boxA, boxB):

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_area = max(0, xB-xA) * max(0, yB-yA)

    areaA = (boxA[2]-boxA[0]) * (boxA[3]-boxA[1])
    areaB = (boxB[2]-boxB[0]) * (boxB[3]-boxB[1])

    union = areaA + areaB - inter_area

    if union == 0:
        return 0

    return inter_area / union


while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % frame_gap != 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        continue

    # frame difference
    diff = cv2.absdiff(gray, prev_gray)

    # contrast stretch
    min_val = np.min(diff)
    max_val = np.max(diff)

    if max_val - min_val != 0:
        diff = ((diff-min_val) * (255/(max_val-min_val))).astype(np.uint8)

    _, motion_mask = cv2.threshold(diff,40,255,cv2.THRESH_BINARY)

    results = model(frame)[0]

    current_boxes = []

    for box in results.boxes:

        x1,y1,x2,y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label_name = model.names[cls]

        current_box = [x1,y1,x2,y2]
        current_boxes.append(current_box)

        motion_region = motion_mask[y1:y2,x1:x2]

        if motion_region.size == 0:
            continue

        motion_score = np.mean(motion_region)

        # IoU comparison
        max_iou = 0
        for prev_box in prev_boxes:
            iou = compute_iou(current_box, prev_box)
            max_iou = max(max_iou, iou)

        if motion_score > 25 and max_iou < 0.8:
            state = "DYNAMIC"
        else:
            state = "STATIC"

        # store history
        key = tuple(current_box)
        history[key].append(state)

        # majority vote
        votes = history[key]
        final_state = max(set(votes), key=votes.count)

        color = (0,255,0) if final_state=="DYNAMIC" else (0,0,255)

        cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)
        cv2.putText(frame,f"{label_name} {final_state}",
                    (x1,y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2)

    prev_boxes = current_boxes
    prev_gray = gray

    cv2.imshow("Stable Static vs Dynamic Detection",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()