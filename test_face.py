import cv2
from deepface import DeepFace

image_path = "faces/ahmed/face_1787221025.jpg"

print("Checking image...")

img = cv2.imread(image_path)

if img is None:
    print("ERROR: OpenCV cannot read the image.")
    exit()

print("Image loaded successfully.")
print("Image size:", img.shape)

try:
    result = DeepFace.extract_faces(
        img_path=image_path,
        detector_backend="opencv",
        enforce_detection=True
    )

    print("Face detected successfully!")
    print("Number of faces:", len(result))

except Exception as e:
    print("DEEPFACE ERROR:")
    print(e)