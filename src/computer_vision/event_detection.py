class EventDetector:
    def __init__(self, raised_hand_detector):
        self.raised_hand_detector = raised_hand_detector

    def detect_events(self, detections, hand_results):
        events = []

        # Phone detection
        phone_detected = any(
            detection["class_name"] == "cell phone"
            for detection in detections
        )

        if phone_detected:
            events.append("phone_detected")

        # Raised hand detection
        if hand_results and hand_results.hand_landmarks:
            for hand_landmarks in hand_results.hand_landmarks:
                if self.raised_hand_detector.is_raised(hand_landmarks):
                    events.append("hand_raised")
                    break

        return events