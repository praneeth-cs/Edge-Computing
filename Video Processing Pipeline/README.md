


# Edge–Cloud Video Processing Pipeline

## 1. Project Overview

This project demonstrates an **edge computing pipeline** where video data is captured and processed locally at the edge device and selectively transmitted to a cloud device. The goal is to reduce unnecessary data transmission by applying **intelligent frame differencing and threshold-based decision making** at the edge.

---

## 2. Objective

- Capture live video at the edge device
- Perform local frame processing
- Reduce redundant data transmission
- Transmit only important information to the cloud
- Quantify data reduction using pixel-level analysis

---

## 3. System Architecture

- **Edge Device:** Mac laptop (camera + processing)
- **Cloud Device:** Windows laptop (Flask server + storage)
- **Network:** Same Wi-Fi hotspot
- **Communication Protocol:** HTTP (Flask)

---

## 4. Project Files

### 4.1 `full_edge_pipeline.py`

**Description:**
- Records a 10-second video at 30 FPS
- Extracts all 300 frames
- Sends every frame to the cloud

**Purpose:**
- Baseline experiment (no edge intelligence)
- Used for comparison with intelligent transmission

---

### 4.2 `intelligent_pipeline.py`

**Description:**
- Records video at the edge
- Computes frame-to-frame differences
- Applies threshold-based transmission logic

**Decision Logic:**

| Frame Difference (%) | Action Taken |
|----------------------|--------------|
| < 1% | Frame not sent |
| 1% – 80% | Delta frame sent |
| ≥ 80% | Full frame (keyframe) sent |

**Purpose:**
- Demonstrates edge-side intelligence
- Reduces unnecessary cloud communication

---

### 4.3 `cloud.py`

**Description:**
- Runs on the cloud laptop
- Receives frames from edge device via HTTP
- Stores received frames in run-specific folders

**Output Structure:**
```

received_frames/
└── run_YYYYMMDD_HHMMSS/
├── keyframe_001.jpg
├── delta_014.jpg
└── ...

```

---

### 4.4 `change_percent.py`

**Description:**
- Analyzes delta frames stored at the edge
- Counts non-zero RGB values
- Computes average percentage of changed pixels

**Formula Used:**
```

Percentage Change =
(non-zero RGB values)
--------------------- × 100
(1920 × 1080 × 3)

````

---

## 5. Experimental Results

- Total frames recorded: **300**
- Delta frames generated: **234**
- Average percentage of changed RGB values in delta frames: **72.36%**
- Average cloud data size per run: **~87 MB**

---

## 6. Key Observations

- Pixel-level comparison is highly sensitive
- Sensor noise and auto-exposure cause changes even in static scenes
- Thresholding at the edge helps filter insignificant data
- Keyframe–delta logic reduces unnecessary full-frame transmission

---

## 7. Conclusion

This project successfully demonstrates an **edge–cloud architecture** where intelligent processing at the edge reduces redundant data transmission. By using frame differencing and thresholds, only meaningful information is sent to the cloud, highlighting the importance of edge computing in real-time video analytics.

---

## 8. How to Run

### Cloud Laptop

```bash
python cloud.py
````

### Edge Laptop (Baseline)

```bash
python edge_full_pipeline.py
```

### Edge Laptop (Intelligent Transmission)

```bash
python edge_intelligent_pipeline.py
```

### Delta Frame Analysis

```bash
python change_percent.py
```

---



**Swadha Singh**
M.tech Artificial Intelligence
Edge Computing Mini Project

```

