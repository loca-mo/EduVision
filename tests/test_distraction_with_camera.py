import cv2

from src.computer_vision.object_detection import ObjectDetector
from src.computer_vision.distraction_detection import DistractionDetector


object_detector = ObjectDetector()
distraction_detector = DistractionDetector()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    # Step 1: Detect objects
    detections = object_detector.detect(frame)

    # Step 2: Analyze possible distractions
    events = distraction_detector.analyze(detections)

    # Step 3: Draw all detected objects
    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        class_name = detection["class_name"]
        confidence = detection["confidence"]

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        label = f"{class_name} {confidence:.2f}"

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Step 4: Display possible distraction
    if events:
        cv2.putText(
            frame,
            "POSSIBLE DISTRACTION",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            3
        )

    cv2.imshow("EduVision - Smart Detection", frame)

    # Press Q on the camera window to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()