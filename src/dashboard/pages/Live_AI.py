import streamlit as st

st.title("🎥 Live AI Vision Feed")
st.caption("Real-Time Classroom Behavior Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    st.camera_input("Camera Feed Simulation")

with col2:
    st.subheader("Live Insights")
    st.success("Camera: Active")
    st.info("Faces Detected: 24")
    st.warning("Distraction Alert: 2 students")