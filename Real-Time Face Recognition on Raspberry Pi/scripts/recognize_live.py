import cv2
import numpy as np
import pickle
import face_recognition

# Load YOLO
net = cv2.dnn.readNet("../models/yolov3-tiny-face.weights", "../models/yolov3-tiny-face.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load encodings
with open("../data/encodings.pkl", "rb") as f:
    data = pickle.load(f)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            confidence = np.max(scores)

            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append((x, y, w, h))

    for (x, y, w, h) in boxes:
        face = frame[y:y+h, x:x+w]

        if face.size == 0:
            continue

        rgb_face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_face)

        name = "Unknown"

        if len(encodings) > 0:
            matches = face_recognition.compare_faces(data["encodings"], encodings[0])

            if True in matches:
                matched_idxs = [i for i, m in enumerate(matches) if m]
                counts = {}

                for i in matched_idxs:
                    counts[data["names"][i]] = counts.get(data["names"][i], 0) + 1

                name = max(counts, key=counts.get)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
