from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path="yolo11n.pt", confidence=0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence

    def detect(self, frame):
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )

        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                class_name = self.model.names[class_id]

                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        return detections