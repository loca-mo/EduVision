import streamlit as st

st.title("⚙️ System Settings")
st.caption("Configure the shared VisionPipeline used by every page.")

pipeline = st.session_state.get("vision_pipeline")

if pipeline is None:
    st.error(
        "Computer Vision pipeline is not available, so settings can't "
        "be applied right now. Check the sidebar for the underlying error."
    )
    st.stop()

st.subheader("Session")

subject = st.text_input(
    "Current Subject / Class",
    value=pipeline.subject,
)

st.subheader("AI Model Configuration")

distance_threshold = st.slider(
    "Face Recognition Distance Threshold (lower = stricter matching)",
    0.1, 0.9,
    pipeline.face_recognizer.distance_threshold,
)

distraction_conf = st.slider(
    "Distraction Alert Sensitivity (min. confidence to flag an object)",
    0.1, 1.0,
    pipeline.distraction_detector.confidence_threshold,
)

st.subheader("Attendance")

min_presence = st.slider(
    "Seconds visible before check-in",
    1, 15,
    pipeline.attendance_manager.min_presence_seconds,
)

grace_period = st.slider(
    "Seconds missing before check-out",
    5, 60,
    pipeline.attendance_manager.grace_period_seconds,
)

if st.button("Save Settings"):
    pipeline.subject = subject
    pipeline.face_recognizer.distance_threshold = distance_threshold
    pipeline.distraction_detector.confidence_threshold = distraction_conf
    pipeline.attendance_manager.min_presence_seconds = min_presence
    pipeline.attendance_manager.grace_period_seconds = grace_period

    st.toast("Settings saved successfully!", icon="✅")
