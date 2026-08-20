import os
import sqlite3
import threading
from datetime import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
from deepface import DeepFace


DATABASE = "eduvision.db"


# ==========================================
# Get students from SQLite
# ==========================================

def get_students():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, student_id, level, department, face_folder
        FROM students
    """)

    students = cursor.fetchall()

    conn.close()

    return students


# ==========================================
# Mark Attendance
# ==========================================

def mark_attendance(student_id):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO attendance
            (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            date,
            time,
            "Present"
        ))

        conn.commit()

        print(f"\nAttendance recorded: {student_id}")
        print(f"Time: {time}")

        result = True

    except sqlite3.IntegrityError:

        print(f"\n{student_id} is already present today.")

        result = False

    conn.close()

    return result


# ==========================================
# Load Students
# ==========================================

students = get_students()

if not students:

    print("ERROR: No students found.")
    exit()


print("\n===================================")
print("     EduVision Attendance System")
print("===================================\n")

print("Registered students:")

for student in students:
    print(f"- {student[0]} (ID: {student[1]})")


# ==========================================
# Camera
# ==========================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():

    print("ERROR: Could not open camera.")
    exit()


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


print("\nCamera started.")
print("Look at the camera.")
print("Press Q or ESC to quit.\n")


# ==========================================
# Recognition variables
# ==========================================

text = "Searching..."
color = (255, 255, 0)

is_checking = False

last_student_id = None


# ==========================================
# Face Recognition Thread
# ==========================================

def recognize_face(frame):

    global text
    global color
    global is_checking
    global last_student_id

    try:

        recognized_student = None
        recognized_id = None


        # Check every registered student
        for student in students:

            name = student[0]
            student_id = student[1]
            face_folder = student[4]


            if not os.path.exists(face_folder):
                continue


            images = []

            for file in os.listdir(face_folder):

                if file.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                ):

                    images.append(
                        os.path.join(face_folder, file)
                    )


            for image_path in images:

                result = DeepFace.verify(

                    img1_path=image_path,

                    img2_path=frame,

                    model_name="Facenet512",

                    detector_backend="opencv",

                    enforce_detection=False
                )


                if result.get("verified", False):

                    recognized_student = name
                    recognized_id = student_id

                    break


            if recognized_student:
                break


        # ==================================
        # Recognized
        # ==================================

        if recognized_student:

            text = f"{recognized_student} - Recognized"
            color = (0, 255, 0)


            # تسجيل الحضور مرة واحدة
            if recognized_id != last_student_id:

                mark_attendance(recognized_id)

                last_student_id = recognized_id


        else:

            text = "Unknown"
            color = (0, 0, 255)

            last_student_id = None


    except Exception as e:

        text = "Searching..."
        color = (255, 255, 0)


    is_checking = False


# ==========================================
# Main Camera Loop
# ==========================================

frame_count = 0


while True:

    ret, frame = cap.read()

    if not ret:

        continue


    # Run recognition in background
    if frame_count % 15 == 0 and not is_checking:

        is_checking = True

        threading.Thread(
            target=recognize_face,
            args=(frame.copy(),),
            daemon=True
        ).start()


    frame_count += 1


    # ======================================
    # Display result
    # ======================================

    cv2.putText(

        frame,

        text,

        (20, 50),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        color,

        2
    )


    cv2.putText(

        frame,

        "Q / ESC = Quit",

        (20, 90),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (255, 255, 255),

        2
    )


    cv2.imshow(

        "EduVision - Attendance System",

        frame
    )


    # ======================================
    # Keyboard
    # ======================================

    key = cv2.waitKey(10) & 0xFF

    if key == ord("q") or key == ord("Q") or key == 27:

        print("\nClosing attendance system...")

        break


# ==========================================
# Close
# ==========================================

cap.release()

cv2.destroyAllWindows()

cv2.waitKey(1)

print("Attendance system closed.")