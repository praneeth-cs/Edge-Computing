import cv2
from ultralytics import YOLO

# Load the lightweight YOLO model (auto-downloads if not present)
model = YOLO("yolov8n.pt")

# Input video
video_path = "video_trimmed.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error opening video file")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Run YOLO inference
    results = model(frame)

    # Draw detection boxes
    annotated_frame = results[0].plot()

    # Display frame
    cv2.imshow("YOLO Object Detection", annotated_frame)

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()