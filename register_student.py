import cv2
import os
import time
import sqlite3

FACES_DIR = "faces"
DATABASE = "eduvision.db"


def register_student():

    # =========================
    # Student Information
    # =========================

    name = input("Enter student name: ").strip()

    if not name:
        print("ERROR: Student name cannot be empty.")
        return

    student_id = input("Enter student ID: ").strip()

    if not student_id:
        print("ERROR: Student ID cannot be empty.")
        return

    level = input("Enter level: ").strip()

    department = input("Enter department: ").strip()


    # =========================
    # Create Student Folder
    # =========================

    student_folder = os.path.join(FACES_DIR, name)

    os.makedirs(student_folder, exist_ok=True)


    # =========================
    # Open Camera
    # =========================

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        return


    print("\nCamera started.")
    print("Look at the camera.")
    print("Press SPACE to capture the face.")
    print("Press Q or ESC to cancel.\n")


    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break


        cv2.putText(
            frame,
            "SPACE = Capture | Q = Quit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        cv2.imshow(
            "EduVision - Student Registration",
            frame
        )


        key = cv2.waitKey(10) & 0xFF


        # =========================
        # Capture Face
        # =========================

        if key == 32:

            file_name = os.path.join(
                student_folder,
                f"face_{int(time.time())}.jpg"
            )


            saved = cv2.imwrite(
                file_name,
                frame
            )


            if not saved:

                print("ERROR: Could not save face image.")
                break


            # =========================
            # Save Student in SQLite
            # =========================

            try:

                conn = sqlite3.connect(DATABASE)

                cursor = conn.cursor()


                cursor.execute("""
                    INSERT INTO students
                    (name, student_id, level, department, face_folder)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    student_id,
                    level,
                    department,
                    student_folder
                ))


                conn.commit()
                conn.close()


                print("\n===================================")
                print("SUCCESS!")
                print("Student registered successfully.")
                print("===================================")

                print("Name:", name)
                print("Student ID:", student_id)
                print("Level:", level)
                print("Department:", department)
                print("Face image:", file_name)


            except sqlite3.IntegrityError:

                print("\nERROR: Student ID already exists.")

            except Exception as e:

                print("\nDATABASE ERROR:")
                print(e)


            break


        # =========================
        # Cancel
        # =========================

        elif key == ord("q") or key == ord("Q") or key == 27:

            print("\nRegistration cancelled.")
            break


    # =========================
    # Close Camera
    # =========================

    camera.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    register_student()