class DistractionDetector:
    """
    Detects possible classroom distractions based on
    objects detected by the object detection module.
    """

    DISTRACTION_OBJECTS = {
        "cell phone",
    }

    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold

    def analyze(self, detections):
        events = []

        for detection in detections:
            class_name = detection["class_name"]
            confidence = detection["confidence"]

            if (
                class_name in self.DISTRACTION_OBJECTS
                and confidence >= self.confidence_threshold
            ):
                events.append({
                    "event_type": "possible_distraction",
                    "object": class_name,
                    "confidence": confidence,
                    "bbox": detection["bbox"],
                })

        return events