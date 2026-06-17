import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Vehicle classes from COCO dataset
vehicle_classes = [2, 3, 5, 7]

video_path = "video_trimmed.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error opening video file")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    boxes = results[0].boxes
    vehicle_count = 0

    # Copy frame for drawing
    annotated_frame = frame.copy()

    for box in boxes:
        cls = int(box.cls[0])

        # Only count vehicles
        if cls in vehicle_classes:
            vehicle_count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[cls]

            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1-5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

    # Display vehicle count
    cv2.putText(
        annotated_frame,
        f"Vehicles in frame: {vehicle_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Traffic Vehicle Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()