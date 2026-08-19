import streamlit as st

st.title("⚙️ System Settings")
st.caption("Configure Cameras, Thresholds, and AI Models")

st.subheader("AI Model Configuration")
st.slider("Face Recognition Confidence Threshold", 0.0, 1.0, 0.75)
st.slider("Distraction Alert Sensitivity", 1, 10, 5)

st.subheader("Camera Setup")
st.text_input("RTSP Stream URL", "rtsp://192.168.1.100:554/stream")

if st.button("Save Settings"):
    st.toast("Settings saved successfully!", icon="✅")