import cv2
import os
import time

# ==============================
# Register New Student
# ==============================

print("===================================")
print("       EduVision Face Registration")
print("===================================")

# اسم الطالب
student_name = input("Enter student name: ").strip()

if not student_name:
    print("ERROR: Student name cannot be empty.")
    exit()

# تنظيف الاسم من الرموز اللي ممكن تعمل مشكلة في Windows
student_name = "".join(
    c for c in student_name
    if c.isalnum() or c in (" ", "_", "-")
).strip()

if not student_name:
    print("ERROR: Invalid student name.")
    exit()

# تحويل المسافات إلى _
folder_name = student_name.replace(" ", "_")

# مكان حفظ الصور
student_folder = os.path.join("faces", folder_name)

# إنشاء المجلد
os.makedirs(student_folder, exist_ok=True)

print(f"\nStudent: {student_name}")
print(f"Saving images in: {student_folder}")

# تشغيل الكاميرا
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

print("\nCamera started.")
print("Look at the camera.")
print("Press SPACE to capture.")
print("Press Q or ESC to cancel.\n")

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Failed to read camera.")
        break

    # عرض التعليمات
    cv2.putText(
        frame,
        "SPACE = Capture | Q = Quit",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow("EduVision - Register Student", frame)

    key = cv2.waitKey(10) & 0xFF

    # SPACE = حفظ الصورة
    if key == 32:

        timestamp = int(time.time())

        image_path = os.path.join(
            student_folder,
            f"face_{timestamp}.jpg"
        )

        cv2.imwrite(image_path, frame)

        print("\nSUCCESS!")
        print(f"Face image saved successfully:")
        print(image_path)
        print("Image size:", frame.shape)

        break

    # Q أو ESC = إلغاء
    elif key == ord("q") or key == ord("Q") or key == 27:

        print("\nRegistration cancelled.")
        break


# إغلاق الكاميرا
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

print("\nRegistration finished.")