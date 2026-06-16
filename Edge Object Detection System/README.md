# Edge Computing Object Detection System

## Project Overview

This project demonstrates a simple edge computing architecture for real-time object detection.

An Android application uploads image frames to Supabase cloud storage.  
A Raspberry Pi OS Virtual Machine acts as an edge node that:

- Polls Supabase for new image frames  
- Runs object detection using YOLOv3-tiny  
- Sends detection results to a Windows host via WebSocket  

The Windows server logs detections in real time.

---

## System Architecture

Android Application  
→ Supabase Storage  
→ Raspberry Pi VM (YOLOv3-tiny Edge Inference)  
→ WebSocket Communication  
→ Windows Server (Detection Logs)

---

# Part 1 – Virtual Machine Setup

## 1. Install VirtualBox

Download and install the latest version of Oracle VirtualBox.

## 2. Download Raspberry Pi Desktop (PC Version)

Download Raspberry Pi Desktop for PC (x86 version).  
Do not use the ARM image.

## 3. Create Virtual Machine

Create a new VM with the following configuration:

- Name: RaspberryEdge  
- Type: Linux  
- Version: Debian (64-bit)  
- RAM: 4GB recommended  
- Storage: 30GB dynamically allocated  

Attach the ISO and complete installation.

---

# Part 2 – Network Configuration

Open:

VirtualBox → VM → Settings → Network

Adapter 1:
- Enabled
- Attached to: NAT

Adapter 2:
- Enabled
- Attached to: Host-only Adapter
- Name: VirtualBox Host-Only Ethernet Adapter

Verify network inside VM:

```bash
ip a
```

You should see:
- 10.0.2.x (NAT)
- 192.168.56.x (Host-only)

If host-only IP is missing, reconfigure the adapter.

---

# Part 3 – Shared Folder Setup

In VirtualBox:

Settings → Shared Folders

- Add Windows project folder
- Enable Auto-mount
- Make Permanent

Inside VM:

```bash
sudo usermod -aG vboxsf $USER
```

Reboot the VM.

Shared folder path:

```
/media/sf_<foldername>/
```

---

# Part 4 – Python Environment Setup (VM)

Update system:

```bash
sudo apt update
sudo apt install python3-venv build-essential libjpeg-dev zlib1g-dev libpng-dev -y
```

Create project directory:

```bash
mkdir ~/edge_vm
cd ~/edge_vm
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Required Libraries

```bash
pip install numpy==1.26.4
pip install opencv-python==4.8.1.78
pip install pillow
pip install requests
pip install websockets
```

Important: NumPy must be version 1.26.4 to avoid OpenCV compatibility errors.

---

# Part 5 – YOLOv3-Tiny Setup

Create models directory:

```bash
mkdir models
cd models
```

Place the following files inside the models folder:

- yolov3-tiny.weights  
- yolov3-tiny.cfg  
- coco.names  

Project structure:

```
edge_vm/
├── vm_poll.py
├── models/
│   ├── yolov3-tiny.weights
│   ├── yolov3-tiny.cfg
│   └── coco.names
```

---

# Part 6 – Supabase Configuration

Inside vm_poll.py, configure:

```python
SUPABASE_URL = "https://your-project-id.supabase.co"
SERVICE_ROLE_KEY = "your_service_role_key"
BUCKET = "video-frames"
```

Bucket structure must follow:

```
video-frames/
   user_id/
      session_id/
         frame_000001.jpg
```

Frames are uploaded every 2 seconds by the Android application.

---

# Part 7 – Windows WebSocket Server Setup

Open Anaconda Prompt.

Create environment:

```bash
conda create -n edge_server python=3.10
conda activate edge_server
pip install websockets
```

Create server.py:

```python
import asyncio
import websockets
import json

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        print("Received:", data)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server started on port 8765")
        await asyncio.Future()

asyncio.run(main())
```

Run the server:

```bash
python server.py
```

---

# Windows Firewall Configuration

- Enable ICMP Echo Request (for ping)
- Allow Python through Private network
- Ensure the VirtualBox Host-only network is set to Private

Test connectivity from VM:

```bash
ping 192.168.56.1
```

If successful, networking is configured correctly.

---

# Running the System

Start Windows server:

```bash
conda activate edge_server
python server.py
```

Start detection engine in VM:

```bash
cd ~/edge_vm
source venv/bin/activate
python vm_poll.py
```

---

# Expected Output

VM terminal:

```
Loading YOLOv3-tiny...
YOLO loaded successfully.
user1/session1 → laptop (0.42)
```

Windows terminal:

```
Received: {'device_id': 'user1', 'session_id': 'session1', 'label': 'laptop', 'confidence': 0.42}
```

---

# Notes

- YOLOv3-tiny is used for lightweight CPU inference.
- Supports up to 5 concurrent devices.
- Session timeout is 30 seconds.
- WebSocket is used for VM to host communication.
- Developed for academic purposes.
