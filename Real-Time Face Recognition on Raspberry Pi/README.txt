Face Recognition System using YOLOv3-tiny and Raspberry Pi

Components:
- YOLOv3-tiny (face detection)
- face_recognition (face identification)
- OpenCV (camera + display)

## Model Files

This project requires the YOLOv3-Tiny Face Detection model files.

### Required Files

Place the following files inside the `models/` directory:

```text
models/
├── yolov3-tiny-face.cfg
├── yolov3-tiny-face.weights
└── face.names
```

### Download YOLOv3-Tiny Face Weights

Download:

`yolov3-tiny-face.weights`

from a trusted YOLO Face Detection repository or release source.

After downloading, place the file in:

```text
models/yolov3-tiny-face.weights
```

### Generate Face Encodings

Before running live recognition, register users and generate face encodings:

```bash
python scripts/register_face.py
python scripts/encode_faces.py
```

This creates:

```text
data/encodings.pkl
```

The encoding file is generated automatically and is not included in the repository.

### Run Face Recognition

```bash
python scripts/recognize_live.py
```


Steps:
1. Install dependencies: pip install -r requirements.txt
2. Run encode_faces.py (if dataset available)
3. Run recognize_live.py for real-time detection

Optional:
- register_face.py to add new faces via camera