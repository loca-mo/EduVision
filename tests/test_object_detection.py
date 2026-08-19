import cv2

from src.computer_vision.object_detection import ObjectDetector
from src.computer_vision.hand_detection import HandDetector
from src.computer_vision.hand_gesture import RaisedHandDetector
from src.computer_vision.event_detection import EventDetector


object_detector = ObjectDetector(
    model_path="yolo11n.pt",
    confidence=0.5,
)

hand_detector = HandDetector()
raised_hand_detector = RaisedHandDetector()

event_detector = EventDetector(
    raised_hand_detector=raised_hand_detector
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera.")
    raise SystemExit


while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read frame.")
        break

    # -------------------------
    # YOLO Object Detection
    # -------------------------
    detections = object_detector.detect(frame)

    frame = object_detector.draw_detections(
        frame,
        detections,
    )

    # -------------------------
    # Hand Detection
    # -------------------------
    hand_results = hand_detector.detect(frame)

    frame = hand_detector.draw_landmarks(
        frame,
        hand_results,
    )

    # -------------------------
    # Event Detection
    # -------------------------
    events = event_detector.detect_events(
        detections,
        hand_results,
    )

    # -------------------------
    # Display Events
    # -------------------------
    y_position = 30

    for event in events:
        cv2.putText(
            frame,
            event,
            (20, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        y_position += 35

    cv2.imshow(
        "EduVision - Computer Vision",
        frame,
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
hand_detector.close()
cv2.destroyAllWindows()
