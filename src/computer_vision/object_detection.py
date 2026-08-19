from pathlib import Path

import cv2
from ultralytics import YOLO


class ObjectDetector:
    def __init__(
        self,
        model_path="yolo11n.pt",
        confidence=0.5,
    ):
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(str(model_path))
        self.confidence = confidence

    def detect(self, frame):
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False,
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist(),
                )

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": result.names[class_id],
                        "confidence": confidence,
                        "bbox": (x1, y1, x2, y2),
                    }
                )

        return detections

    def draw_detections(self, frame, detections):
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]

            label = (
                f'{detection["class_name"]} '
                f'{detection["confidence"]:.2f}'
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return frame

    def is_person_detected(self, detections):
        return any(
            detection["class_name"] == "person"
            for detection in detections
        )

    def is_phone_detected(self, detections):
        return any(
            detection["class_name"] == "cell phone"
            for detection in detections
        )