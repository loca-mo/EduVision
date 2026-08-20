from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolo11n.pt")

# Open camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    # Run YOLO detection
    results = model(frame, verbose=False)

    # Draw detections
    annotated_frame = results[0].plot()

    cv2.imshow("EduVision - YOLO Detection", annotated_frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()