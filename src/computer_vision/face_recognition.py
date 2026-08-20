import os

# لازم يكون قبل استيراد DeepFace/TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
from deepface import DeepFace


# صورة أحمد المرجعية
reference_image = "faces/ahmed/face_1787221025.jpg"

if not os.path.exists(reference_image):
    print(f"Error: Reference image not found: {reference_image}")
    exit()


# تشغيل الكاميرا
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera failed to open.")
    exit()


print("Camera started.")
print("Look at the camera.")
print("Press Q or ESC to quit.")


text = "Searching..."
color = (255, 255, 0)

frame_count = 0


while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read camera.")
        break


    # فحص الوجه كل 15 فريم
    if frame_count % 15 == 0:

        try:

            result = DeepFace.verify(
                img1_path=reference_image,
                img2_path=frame,
                model_name="Facenet512",
                detector_backend="opencv",
                enforce_detection=False
            )

            if result.get("verified", False):

                text = "Ahmed - Recognized"
                color = (0, 255, 0)

            else:

                text = "Unknown"
                color = (0, 0, 255)


        except Exception:

            text = "Searching..."
            color = (255, 255, 0)


    frame_count += 1


    # كتابة النتيجة
    cv2.putText(
        frame,
        text,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )


    # عرض النتيجة
    cv2.imshow(
        "EduVision - Face Recognition",
        frame
    )


    # قراءة الكيبورد
    key = cv2.waitKey(10) & 0xFF

    if key == ord("q") or key == ord("Q") or key == 27:
        print("Closing camera...")
        break


# إغلاق الكاميرا والنوافذ
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)