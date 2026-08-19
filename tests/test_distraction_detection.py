from src.computer_vision.distraction_detection import DistractionDetector


detector = DistractionDetector()

detections = [
    {
        "class_name": "cell phone",
        "confidence": 0.87,
        "bbox": [100, 150, 200, 300],
    }
]

events = detector.analyze(detections)

print("Detected events:")
for event in events:
    print(event)