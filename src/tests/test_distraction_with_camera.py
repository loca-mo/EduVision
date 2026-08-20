import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from src.computer_vision.object_detection import ObjectDetector
from src.computer_vision.distraction_detection import DistractionDetector


class EduVisionProcessor(VideoProcessorBase):
    def __init__(self):
        self.object_detector = ObjectDetector()
        self.distraction_detector = DistractionDetector()

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")

        # Step 1: Detect objects
        detections = self.object_detector.detect(image)

        # Step 2: Analyze possible distractions
        events = self.distraction_detector.analyze(detections)

        # Step 3: Draw detected objects
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            class_name = detection["class_name"]
            confidence = detection["confidence"]

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            label = f"{class_name} {confidence:.2f}"

            cv2.putText(
                image,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # Step 4: Display distraction warning
        if events:
            cv2.putText(
                image,
                "POSSIBLE DISTRACTION",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3,
            )

        return frame.from_ndarray(image, format="bgr24")


st.title("EduVision - Smart Detection")

st.write(
    "Allow camera access in your browser to start real-time "
    "object and distraction detection."
)

webrtc_streamer(
    key="eduvision-camera",
    video_processor_factory=EduVisionProcessor,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
    async_processing=True,
)