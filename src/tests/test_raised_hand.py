import cv2

from src.computer_vision.hand_detection import HandDetector


hand_detector = HandDetector()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    results = hand_detector.detect(frame)

    frame = hand_detector.draw_landmarks(frame, results)

    if results.hand_landmarks:
        for hand_landmarks in results.hand_landmarks:
            wrist = hand_landmarks[0]

            print(f"Wrist Y: {wrist.y:.3f}")

            if wrist.y < 0.45:
                cv2.putText(
                    frame,
                    "HAND RAISED",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3,
                )

    cv2.imshow("EduVision - Raised Hand Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
hand_detector.close()
cv2.destroyAllWindows()