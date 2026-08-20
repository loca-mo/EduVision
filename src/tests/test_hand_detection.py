import cv2

from src.computer_vision.hand_detection import HandDetector


detector = HandDetector()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera.")
    detector.close()
    raise SystemExit


while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    results = detector.detect(frame)

    frame = detector.draw_landmarks(frame, results)

    cv2.imshow("EduVision - Hand Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
detector.close()
cv2.destroyAllWindows()