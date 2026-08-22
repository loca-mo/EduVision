from pathlib import Path

import cv2
from ultralytics import YOLO


class ObjectDetector:
    """
    Fast classroom object detector for EduVision.

    Detects useful COCO objects such as:
        - person
        - cell phone
        - laptop
        - book
        - backpack
        - bottle
        - cup

    The detector is optimized to:
        - reduce unnecessary detections
        - control inference image size
        - use a confidence threshold
        - optionally detect only useful classes
        - return clean bounding boxes
    """

    # COCO class IDs used by YOLO
    CLASS_IDS = {
        "person": 0,
        "backpack": 24,
        "bottle": 39,
        "cup": 41,
        "book": 73,
        "laptop": 63,
        "cell phone": 67,
    }

    # Objects EduVision actually cares about.
    USEFUL_CLASSES = {
        "person",
        "cell phone",
        "laptop",
        "book",
        "backpack",
        "bottle",
        "cup",
    }

    def __init__(
        self,
        model_path="yolo11n.pt",
        confidence=0.45,
        image_size=640,
        device=None,
        detect_every=2,
    ):
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(
            str(model_path)
        )

        self.confidence = confidence

        # 640 is a good compromise between
        # accuracy and speed.
        self.image_size = image_size

        # None lets Ultralytics choose.
        # You can set "cpu", "0", etc.
        self.device = device

        # Don't run YOLO on every single frame.
        self.detect_every = max(
            1,
            int(detect_every)
        )

        self._frame_count = 0

        self._last_detections = []

        self.last_processing_time = 0.0

    # ============================================================
    # DETECTION
    # ============================================================

    def detect(self, frame):
        """
        Detect objects in a frame.

        Results are cached between inference frames to reduce lag.
        """

        self._frame_count += 1

        # --------------------------------------------------------
        # Return cached detections
        # --------------------------------------------------------

        if (
            self._frame_count != 1
            and
            self._frame_count
            %
            self.detect_every
            != 0
        ):
            return self._last_detections

        # --------------------------------------------------------
        # Run YOLO
        # --------------------------------------------------------

        import time

        start_time = time.perf_counter()

        try:

            results = self.model(
                frame,

                # Image size used internally by YOLO.
                imgsz=self.image_size,

                # Confidence threshold.
                conf=self.confidence,

                # Only detect useful COCO classes.
                classes=[
                    self.CLASS_IDS[name]
                    for name in self.USEFUL_CLASSES
                ],

                # Prevent unnecessary console output.
                verbose=False,

                # Use selected device.
                device=self.device,
            )

        except Exception as e:

            print(
                f"YOLO detection failed: {e}"
            )

            return self._last_detections

        detections = []

        # --------------------------------------------------------
        # Parse YOLO results
        # --------------------------------------------------------

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                # ------------------------------------------------
                # Extra confidence filtering
                # ------------------------------------------------

                if confidence < self.confidence:
                    continue

                # ------------------------------------------------
                # Bounding box
                # ------------------------------------------------

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist(),
                )

                # ------------------------------------------------
                # Clamp coordinates to image
                # ------------------------------------------------

                height, width = (
                    frame.shape[:2]
                )

                x1 = max(
                    0,
                    min(x1, width - 1)
                )

                y1 = max(
                    0,
                    min(y1, height - 1)
                )

                x2 = max(
                    0,
                    min(x2, width - 1)
                )

                y2 = max(
                    0,
                    min(y2, height - 1)
                )

                if x2 <= x1 or y2 <= y1:
                    continue

                # ------------------------------------------------
                # Class name
                # ------------------------------------------------

                class_name = result.names.get(
                    class_id,
                    str(class_id)
                )

                # ------------------------------------------------
                # Keep useful objects only
                # ------------------------------------------------

                if (
                    class_name
                    not in self.USEFUL_CLASSES
                ):
                    continue

                detections.append(
                    {
                        "class_id": class_id,

                        "class_name": class_name,

                        "confidence": round(
                            confidence,
                            3
                        ),

                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2,
                        ),
                    }
                )

        # --------------------------------------------------------
        # Save cache
        # --------------------------------------------------------

        self._last_detections = detections

        self.last_processing_time = (
            time.perf_counter()
            -
            start_time
        )

        return detections

    # ============================================================
    # DRAW DETECTIONS
    # ============================================================

    def draw_detections(
        self,
        frame,
        detections
    ):

        for detection in detections:

            x1, y1, x2, y2 = (
                detection["bbox"]
            )

            class_name = (
                detection["class_name"]
            )

            confidence = (
                detection["confidence"]
            )

            # ----------------------------------------------------
            # Different visual treatment
            # ----------------------------------------------------

            if class_name == "cell phone":

                color = (
                    0,
                    0,
                    255
                )

            elif class_name == "person":

                color = (
                    0,
                    255,
                    0
                )

            else:

                color = (
                    255,
                    255,
                    0
                )

            label = (
                f"{class_name} "
                f"{confidence:.2f}"
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2,
            )

            cv2.putText(
                frame,
                label,
                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    ),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
            )

        return frame

    # ============================================================
    # CLASS FILTER
    # ============================================================

    def get_objects(
        self,
        detections,
        class_name
    ):

        return [
            detection
            for detection in detections
            if detection["class_name"]
            == class_name
        ]

    # ============================================================
    # PERSONS
    # ============================================================

    def get_people(
        self,
        detections
    ):

        return self.get_objects(
            detections,
            "person"
        )

    # ============================================================
    # PHONES
    # ============================================================

    def get_phones(
        self,
        detections
    ):

        return self.get_objects(
            detections,
            "cell phone"
        )

    # ============================================================
    # LAPTOPS
    # ============================================================

    def get_laptops(
        self,
        detections
    ):

        return self.get_objects(
            detections,
            "laptop"
        )

    # ============================================================
    # BOOKS
    # ============================================================

    def get_books(
        self,
        detections
    ):

        return self.get_objects(
            detections,
            "book"
        )

    # ============================================================
    # SIMPLE CHECKS
    # ============================================================

    def is_person_detected(
        self,
        detections
    ):

        return any(
            detection["class_name"]
            == "person"
            for detection in detections
        )

    def is_phone_detected(
        self,
        detections
    ):

        return any(
            detection["class_name"]
            == "cell phone"
            for detection in detections
        )

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        return {
            "model": str(
                self.model
            ),

            "confidence": (
                self.confidence
            ),

            "image_size": (
                self.image_size
            ),

            "detect_every": (
                self.detect_every
            ),

            "last_processing_time": round(
                self.last_processing_time,
                3
            ),

            "cached_objects": len(
                self._last_detections
            ),
        }