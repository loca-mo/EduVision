import streamlit as st

st.title("✋ Classroom Interaction")
st.caption("Monitoring Hand Raises, Participation, and Activity")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Hand Raises Today", "48")
    st.progress(0.75, text="Target Participation Rate (75%)")

with col2:
    st.metric("Active Speakers", "14 Students")
    st.progress(0.60, text="Group Discussion Balance")