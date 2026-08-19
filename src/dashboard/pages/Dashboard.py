import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Executive Dashboard")
st.caption("Real-time Overview of Classroom Metrics")

# Key Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Classes", "12", "+2 today")
c2.metric("Avg Attendance", "94.2%", "+1.5%")
c3.metric("Engagement Score", "87%", "+5%")
c4.metric("OCR Scans Today", "342", "+28")

st.divider()

# Demo Chart
chart_data = pd.DataFrame({
    "Time": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"],
    "Engagement": [65, 82, 91, 78, 85, 90]
})
fig = px.line(chart_data, x="Time", y="Engagement", title="Hourly Student Engagement Trend", markers=True)
st.plotly_chart(fig, use_container_width=True)