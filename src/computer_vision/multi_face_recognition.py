import os

# إخفاء رسائل TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
from deepface import DeepFace


# ==============================
# EduVision - Multi Student Face Recognition
# ==============================

FACES_FOLDER = "faces"


# التأكد من وجود مجلد الطلاب
if not os.path.exists(FACES_FOLDER):
    print("ERROR: faces folder not found.")
    exit()


# قراءة الطلاب المسجلين
students = {}

for student_name in os.listdir(FACES_FOLDER):

    student_folder = os.path.join(FACES_FOLDER, student_name)

    if not os.path.isdir(student_folder):
        continue

    images = []

    for file in os.listdir(student_folder):

        if file.lower().endswith((".jpg", ".jpeg", ".png")):

            images.append(
                os.path.join(student_folder, file)
            )

    if images:
        students[student_name] = images


# التأكد من وجود طلاب
if not students:
    print("ERROR: No students found.")
    exit()


print("\n==============================")
print("EduVision Face Recognition")
print("==============================")

print("\nRegistered students:")

for student in students:
    print("-", student)

print("\nStarting camera...")
print("Look at the camera.")
print("Press Q or ESC to quit.\n")


# تشغيل الكاميرا
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()


text = "Looking..."
color = (255, 255, 0)

frame_count = 0


while True:

    ret, frame = cap.read()

    if not ret:
        continue


    # الفحص كل 15 Frame
    if frame_count % 15 == 0:

        try:

            recognized_student = None


            # تجربة كل طالب
            for student_name, images in students.items():

                for image_path in images:

                    result = DeepFace.verify(
                        img1_path=image_path,
                        img2_path=frame,
                        model_name="Facenet512",
                        detector_backend="opencv",
                        enforce_detection=False
                    )

                    if result.get("verified", False):

                        recognized_student = student_name
                        break

                if recognized_student:
                    break


            # النتيجة
            if recognized_student:

                display_name = recognized_student.replace("_", " ")

                text = f"{display_name} - Recognized"
                color = (0, 255, 0)

            else:

                text = "Unknown"
                color = (0, 0, 255)


        except Exception as e:

            text = "Searching..."
            color = (255, 255, 0)


    frame_count += 1


    # عرض النتيجة
    cv2.putText(
        frame,
        text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2
    )


    cv2.imshow(
        "EduVision - Multi Face Recognition",
        frame
    )


    # Q أو ESC
    key = cv2.waitKey(10) & 0xFF

    if key == ord("q") or key == ord("Q") or key == 27:

        print("Closing camera...")
        break


# إغلاق
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

print("Camera closed.")