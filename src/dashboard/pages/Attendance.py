import streamlit as st
import pandas as pd

st.title("👥 Attendance Tracking")
st.caption("Automated Face Recognition & Attendance Logs")

data = pd.DataFrame({
    "Student ID": ["ST001", "ST002", "ST003", "ST004"],
    "Name": ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince"],
    "Status": ["Present", "Present", "Absent", "Late"],
    "Time In": ["08:58 AM", "09:01 AM", "-", "09:15 AM"]
})

st.dataframe(data, use_container_width=True)