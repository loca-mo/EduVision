"""
Live AI Vision Feed
--------------------
This page owns the actual camera loop: it reads frames from the shared
CameraManager, runs them through the shared VisionPipeline, and displays
the annotated feed + live counts.
 
Every other page (Dashboard, Attendance, Interaction) just reads
`pipeline.last_result` — the numbers on those pages update whenever this
page has run the camera at least once.
"""
 
import sys
import time
from pathlib import Path
 
import cv2
import streamlit as st
 
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
 
from src.computer_vision.camera_manager import CameraManager
 
 
st.title("🎥 Live AI Vision Feed")
st.caption("Real-Time Classroom Behavior Analysis")
 
pipeline = st.session_state.get("vision_pipeline")
vision_ready = st.session_state.get("vision_initialized", False)
 
if not vision_ready or pipeline is None:
    st.error(
        "Computer Vision pipeline is not available. "
        "Check the sidebar / Settings page for the underlying error."
    )
    st.stop()
 
camera = CameraManager()
 
col1, col2 = st.columns([3, 1])
 
with col1:
    run_camera = st.toggle("Start Camera", value=False)
    frame_slot = st.empty()
 
with col2:
    st.subheader("Live Insights")
    people_slot = st.empty()
    focus_slot = st.empty()
    distraction_slot = st.empty()
    hands_slot = st.empty()
    error_slot = st.empty()
 
if not run_camera:
    st.info("Toggle **Start Camera** to begin live monitoring.")
 
    if pipeline.last_result:
        result = pipeline.last_result
        people_slot.metric("Students Detected (last frame)", result["people_count"])
        focus_slot.metric("Average Focus (last frame)", f'{result["average_focus"]:.0f}%')
        distraction_slot.metric("Distractions (last frame)", result["distraction_count"])
        hands_slot.metric("Raised Hands (last frame)", result["raised_hands"])
 
else:
    camera.open()
 
    if not camera.is_opened():
        st.error("Could not open the camera.")
 
    else:
        # Streamlit has no built-in "keep this loop running forever"
        # primitive without extra dependencies (e.g. streamlit-webrtc).
        # As a lightweight alternative, we process a batch of frames per
        # script run, then st.rerun() to loop again as long as the
        # toggle stays on.
        consecutive_failures = 0
 
        for _ in range(150):
 
            ret, frame = camera.read()
 
            if not ret:
                consecutive_failures += 1
                if consecutive_failures >= 20:
                    st.warning("Failed to read from camera.")
                    break
                time.sleep(0.03)
                continue
 
            consecutive_failures = 0
 
            result = pipeline.process_frame(frame)
            annotated = pipeline.draw_annotations(frame.copy())
            annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
 
            frame_slot.image(annotated_rgb, use_container_width=True)
 
            people_slot.metric("Students Detected", result["people_count"])
            focus_slot.metric("Average Focus", f'{result["average_focus"]:.0f}%')
            distraction_slot.metric("Distractions", result["distraction_count"])
            hands_slot.metric("Raised Hands", result["raised_hands"])
 
            face_error = pipeline.face_recognizer.last_error
            if face_error:
                error_slot.error(f"Face recognition error: {face_error}")
            else:
                error_slot.empty()
 
            time.sleep(0.03)
 
        st.rerun()
 