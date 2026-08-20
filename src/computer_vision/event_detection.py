class EventDetector:
    def __init__(self, raised_hand_detector, distraction_detector):
        self.raised_hand_detector = raised_hand_detector
        self.distraction_detector = distraction_detector

    def detect_events(self, detections, hand_results):
        events = []

        # Phone detected
        if any(
            detection["class_name"] == "cell phone"
            for detection in detections
        ):
            events.append("phone_detected")

        # Raised hand detected
        if hand_results and hand_results.hand_landmarks:
            for hand_landmarks in hand_results.hand_landmarks:
                if self.raised_hand_detector.is_raised(hand_landmarks):
                    events.append("hand_raised")
                    break

        # Distraction detection
        distraction_events = self.distraction_detector.analyze(
            detections
        )

        for event in distraction_events:
            events.append(event["event_type"])

        return events