import cv2
import os
import time

FACES_DIR = "faces"


def register_student():

    name = input("Enter student name: ").strip()

    if not name:
        print("ERROR: Student name cannot be empty.")
        return

    student_folder = os.path.join(FACES_DIR, name)
    os.makedirs(student_folder, exist_ok=True)

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        return

    # Set camera resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\nCamera started.")
    print("Look at the camera.")
    print("Press SPACE to capture.")
    print("Press Q to quit.\n")

    # Wait for a valid frame
    frame = None

    for _ in range(30):
        success, test_frame = camera.read()

        if success and test_frame is not None:
            frame = test_frame
            break

        time.sleep(0.1)

    if frame is None:
        print("ERROR: Camera is not returning frames.")
        camera.release()
        return

    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break

        display_frame = frame.copy()

        cv2.putText(
            display_frame,
            "SPACE = Capture | Q = Quit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("EduVision - Student Registration", display_frame)

        key = cv2.waitKey(1) & 0xFF

        # SPACE
        if key == 32:

            file_name = os.path.join(
                student_folder,
                f"face_{int(time.time())}.jpg"
            )

            saved = cv2.imwrite(file_name, frame)

            if saved and os.path.exists(file_name):

                # Check saved image size
                saved_image = cv2.imread(file_name)

                if saved_image is not None:
                    print("\nSUCCESS!")
                    print("Face image saved successfully:")
                    print(file_name)
                    print("Image size:", saved_image.shape)

                else:
                    print("ERROR: Image was saved but cannot be read.")

            else:
                print("ERROR: Failed to save image.")

            break

        # Q
        elif key == ord("q"):
            print("\nRegistration cancelled.")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    register_student()