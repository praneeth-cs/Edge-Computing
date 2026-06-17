import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

video_path = "video_trimmed.mp4"
cap = cv2.VideoCapture(video_path)

incoming = 0
outgoing = 0

vehicle_classes = {2,3,5,7}

# store previous positions
track_history = {}

# store line crossing states
cross_state = {}

while True:

    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    # slightly raised lines
    L1 = int(h * 0.55)
    L2 = int(h * 0.70)

    cv2.line(frame,(0,L1),(w,L1),(255,255,255),3)
    cv2.line(frame,(0,L2),(w,L2),(255,255,255),3)

    results = model.track(frame, persist=True)[0]

    if results.boxes.id is None:
        cv2.imshow("Vehicle Counter",frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        continue

    boxes = results.boxes.xyxy.cpu().numpy()
    ids = results.boxes.id.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy()

    for box,obj_id,cls in zip(boxes,ids,classes):

        if int(cls) not in vehicle_classes:
            continue

        obj_id = int(obj_id)

        x1,y1,x2,y2 = map(int,box)

        center_y = int((y1+y2)/2)
        center_x = int((x1+x2)/2)

        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.circle(frame,(center_x,center_y),4,(0,255,0),-1)

        if obj_id not in track_history:
            track_history[obj_id] = center_y
            cross_state[obj_id] = None

        prev_y = track_history[obj_id]

        # detect L1 crossing
        if prev_y < L1 and center_y >= L1:
            cross_state[obj_id] = "L1"

        # detect L2 crossing
        elif prev_y > L2 and center_y <= L2:
            cross_state[obj_id] = "L2"

        # outgoing vehicles
        if cross_state[obj_id] == "L1" and center_y > L2:
            outgoing += 1
            cross_state[obj_id] = "counted"

        # incoming vehicles
        if cross_state[obj_id] == "L2" and center_y < L1:
            incoming += 1
            cross_state[obj_id] = "counted"

        track_history[obj_id] = center_y

    cv2.putText(frame,f"Incoming: {incoming}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2)

    cv2.putText(frame,f"Outgoing: {outgoing}",
                (20,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2)

    cv2.imshow("Vehicle Counter",frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()