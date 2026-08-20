from src.computer_vision.distraction_detection import DistractionDetector


def test_phone_distraction():
    detector = DistractionDetector()

    detections = [
        {
            "class_name": "cell phone",
            "confidence": 0.87,
            "bbox": [100, 150, 200, 300],
        }
    ]

    events = detector.analyze(detections)

    assert len(events) == 1
    assert events[0]["event_type"] == "possible_distraction"
    assert events[0]["object"] == "cell phone"
    assert events[0]["confidence"] == 0.87

    print("Phone distraction test: PASSED")


def test_low_confidence_phone():
    detector = DistractionDetector()

    detections = [
        {
            "class_name": "cell phone",
            "confidence": 0.3,
            "bbox": [100, 150, 200, 300],
        }
    ]

    events = detector.analyze(detections)

    assert len(events) == 0

    print("Low-confidence test: PASSED")


if __name__ == "__main__":
    test_phone_distraction()
    test_low_confidence_phone()