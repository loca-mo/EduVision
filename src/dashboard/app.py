import streamlit as st

#######################
# Page configuration
st.set_page_config(
    page_title="EduVision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

#######################
# Pages (linked to your existing files in src/dashboard/pages)
dashboard_page = st.Page("pages/Dashboard.py", title="Dashboard", icon="📊", default=True)
attendance_page = st.Page("pages/Attendance.py", title="Attendance", icon="🧍")
interaction_page = st.Page("pages/Interaction.py", title="Interaction", icon="💬")
live_ai_page = st.Page("pages/Live_AI.py", title="Live AI", icon="🎥")
ocr_notes_page = st.Page("pages/OCR_Notes.py", title="OCR Notes", icon="📝")
ai_assistant = st.Page("pages/AI_Assistant.py", title="AI & Voice Assistant", icon="🤖")
reports_page = st.Page("pages/Reports.py", title="Reports", icon="📄")
settings_page = st.Page("pages/Settings.py", title="Settings", icon="⚙️")

pg = st.navigation(
    {
        "Overview": [dashboard_page],
        "Classroom": [attendance_page, interaction_page, live_ai_page, ocr_notes_page, ai_assistant],
        "Insights": [reports_page],
        "App": [settings_page],
    }
)

#######################
# Sidebar
with st.sidebar:
    st.title("🎓 EduVision")
    st.caption("Smart classroom monitoring & reporting")

    st.subheader("Team")
    st.markdown(
        " Malak Hossam\n"
        " Roqaya Mohamed\n"
        " Sara Elsayed"
    )

#######################
# Run selected page
pg.run()