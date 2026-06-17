# Road Traffic Object Detection

## Overview

Road Traffic Object Detection is a computer vision project that applies YOLOv8 and OpenCV techniques to analyze traffic video footage. The project progresses from basic object detection to advanced traffic flow analysis by identifying moving vehicles, classifying motion behavior, and counting incoming and outgoing vehicles.

## Project Objectives

- Detect road objects using YOLOv8
- Identify vehicle classes from detected objects
- Extract moving vehicles from traffic footage
- Classify vehicles as static or dynamic
- Improve motion classification stability across frames
- Analyze traffic flow through vehicle counting

## Project Workflow

### Step 1: Video Preparation
- Collect and prepare traffic video footage
- Extract and inspect frames for analysis

### Step 2: Object Detection
- Detect objects using YOLOv8
- Draw bounding boxes around detected objects

### Step 3: Vehicle Detection and Counting
- Filter detections to vehicle categories
- Count vehicles present in each frame

### Step 4: Moving Vehicle Extraction
- Apply frame differencing techniques
- Remove stationary background regions
- Highlight moving vehicles only

### Step 5: Static vs Dynamic Vehicle Classification
- Analyze motion within detected vehicle regions
- Label vehicles as STATIC or DYNAMIC

### Step 6: Stable Motion Analysis
- Use IoU matching and motion history
- Reduce classification flickering
- Improve consistency across frames

### Step 7: Incoming and Outgoing Vehicle Counting
- Track vehicle movement across defined boundaries
- Count vehicles entering the monitored region
- Count vehicles leaving the monitored region
- Generate traffic flow statistics

## Technologies Used

- Python
- YOLOv8 (Ultralytics)
- OpenCV
- NumPy

## Installation

pip install -r requirements.txt

## License

Educational and research purposes.
