# YOLO Detector
import cv2
from ultralytics import YOLO
import numpy as np


class VideoDetector:
    def __init__(self, model_path="models/yolov8n.pt"):
        self.model = YOLO(model_path)  # Load the YOLO model
        # Generate colors for bounding boxes
        self.colors = self._generate_colors(80)

    def _generate_colors(self, n):
        np.random.seed(42)  # For reproducibility
        return [tuple(int(c) for c in color)
                for color in np.random.randint(0, 255, (n, 3))]

    def detect_frame(self, frame):
        """Detect objects in a single frame and return the annotated frame."""

        # Run detection on the frame
        results = self.model(frame, persist=True, verbose=False, imgsz=640)
        annotated = frame.copy()

        if results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                track_id = int(box.id[0]) if box.id is not None else -1
                label = self.model.names[cls]
                color = self.colors[cls % len(self.colors)]

                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                # Draw label background
                text = f"#{track_id} {label} {conf:.2f}"
                (tw, th), _ = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
                cv2.rectangle(annotated, (x1, y1 - th - 8),
                              (x1 + tw + 4, y1), color, -1)
                cv2.putText(annotated, text, (x1 + 2, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        return annotated, results[0]

    def process_video(self, input_path, output_path):
        """Process a full video file. Returns detection summary."""
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        out = cv2.VideoWriter(output_path,
                              cv2.VideoWriter_fourcc(*"mp4v"),
                              fps, (w, h))
        frame_count = 0
        detection_log = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            annotated, result = self.detect_frame(frame)
            out.write(annotated)
            frame_count += 1

            if result.boxes is not None and len(result.boxes):
                objs = [self.model.names[int(b.cls[0])] for b in result.boxes]
                detection_log.append({"frame": frame_count, "objects": objs})

        cap.release()
        out.release()
        return {"frames": frame_count, "detections": detection_log}

    def stream_frames(self, source=0):
        """Generator: yields JPEG bytes for MJPEG streaming. source=0 for webcam."""
        cap = cv2.VideoCapture(source)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            annotated, _ = self.detect_frame(frame)
            _, buffer = cv2.imencode(
                ".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                   + buffer.tobytes() + b"\r\n")
        cap.release()
