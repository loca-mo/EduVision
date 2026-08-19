import cv2

from src.computer_vision.object_detection import ObjectDetector


detector = ObjectDetector()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    detections = detector.detect(frame)

    # Draw detections
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

    cv2.imshow("EduVision - Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()