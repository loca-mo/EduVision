import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetector:
    def __init__(
        self,
        model_path="models/hand_landmarker.task",
        num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        results = self.detector.detect(mp_image)

        return results

    def draw_landmarks(self, frame, results):
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:

                height, width, _ = frame.shape

                points = []

                for landmark in hand_landmarks:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    points.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

                # Draw connections between landmarks
                for connection in vision.HandLandmarksConnections.HAND_CONNECTIONS:
                    start = connection.start
                    end = connection.end

                    cv2.line(
                        frame,
                        points[start],
                        points[end],
                        (0, 255, 0),
                        2
                    )

        return frame

    def close(self):
        self.detector.close()