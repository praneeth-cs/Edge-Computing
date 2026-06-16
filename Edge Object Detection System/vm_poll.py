import requests
import io
import json
import asyncio
import websockets
import cv2
import numpy as np
from PIL import Image
from datetime import datetime, timezone

# ================= CONFIG =================

SUPABASE_URL = "https://oqimttobcznhxnawhhsu.supabase.co"
SERVICE_ROLE_KEY = "Enter your key here"
BUCKET = "video-frames"

WINDOWS_WS_SERVER = "ws://192.168.56.1:8765"

SESSION_TIMEOUT = 30
CONF_THRESHOLD = 0.2

HEADERS = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
}

print("Loading YOLOv3-tiny...")

net = cv2.dnn.readNet(
    "models/yolov3-tiny.weights",
    "models/yolov3-tiny.cfg"
)

with open("models/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

print("YOLO loaded successfully.")
print("=== Edge Detection Engine Started ===")

# ================= HELPERS =================

def list_path(prefix=""):
    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET}"
    payload = {"prefix": prefix}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 200:
        return []
    return response.json()

def download_frame(user_id, session_id, frame_name):
    path = f"{BUCKET}/{user_id}/{session_id}/{frame_name}"
    url = f"{SUPABASE_URL}/storage/v1/object/{path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return None
    image = Image.open(io.BytesIO(response.content))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def detect_objects(frame):
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    best_label = "No Object Detected"
    best_conf = 0

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > CONF_THRESHOLD and confidence > best_conf:
                best_conf = float(confidence)
                best_label = classes[class_id]

    return best_label, best_conf

async def send_detection(payload):
    try:
        async with websockets.connect(WINDOWS_WS_SERVER) as websocket:
            await websocket.send(json.dumps(payload))
    except Exception as e:
        print("WebSocket send failed:", e)

# ================= MAIN =================

users = [item["name"] for item in list_path("") if item.get("id") is None]

active_sessions = []

# -------- CHECK ACTIVE --------

for user in users:
    sessions = [item["name"] for item in list_path(user) if item.get("id") is None]

    for session in sessions:
        items = list_path(f"{user}/{session}")
        files = [item for item in items if item.get("id")]

        if not files:
            continue

        files.sort(key=lambda x: x["name"])
        latest = files[-1]

        updated_dt = datetime.fromisoformat(
            latest["updated_at"].replace("Z", "+00:00")
        )
        now = datetime.now(timezone.utc)

        if (now - updated_dt).total_seconds() <= SESSION_TIMEOUT:
            active_sessions.append((user, session, latest["name"]))

# -------- LIVE MODE --------

if active_sessions:
    print("Active sessions found.")

    for user, session, frame_name in active_sessions:
        frame = download_frame(user, session, frame_name)
        if frame is None:
            continue

        label, confidence = detect_objects(frame)
        print(f"[LIVE] {user}/{session} → {label} ({confidence:.2f})")

        payload = {
            "device_id": user,
            "session_id": session,
            "label": label,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "active": True
        }

        asyncio.run(send_detection(payload))

# -------- BATCH MODE --------

else:
    print("No active sessions. Running batch mode.")

    for user in users:
        sessions = [item["name"] for item in list_path(user) if item.get("id") is None]

        for session in sessions:
            items = list_path(f"{user}/{session}")
            files = [item for item in items if item.get("id")]

            files.sort(key=lambda x: x["name"])

            for file in files:
                frame = download_frame(user, session, file["name"])
                if frame is None:
                    continue

                label, confidence = detect_objects(frame)
                print(f"[BATCH] {user}/{session}/{file['name']} → {label} ({confidence:.2f})")

                payload = {
                    "device_id": user,
                    "session_id": session,
                    "label": label,
                    "confidence": confidence,
                    "timestamp": datetime.utcnow().isoformat(),
                    "active": False
                }

                asyncio.run(send_detection(payload))

print("Processing complete.")
