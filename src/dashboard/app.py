import streamlit as st
 
st.set_page_config(
    page_title="EduVision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ---------------------------------------------------------------------------
# Initialize state shared across all pages (used by any team module)
# ---------------------------------------------------------------------------
if "current_subject" not in st.session_state:
    st.session_state["current_subject"] = None
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "guest"
 
# ---------------------------------------------------------------------------
# Register pages in a clear order (mine + the team's)
# Update your teammates' filenames here if they differ from what's expected
# ---------------------------------------------------------------------------
pages = {
    "Home": [
        st.Page("pages/Dashboard.py", title="Dashboard", icon="🏠"),
    ],
    "My part (OCR + Attendance + Events + Reports)": [
        st.Page("pages/OCR_Notes.py", title="Blackboard Reading", icon="📝"),
        st.Page("pages/Attendance.py", title="Attendance", icon="✅"),
        st.Page("pages/Interaction.py", title="Events", icon="⚡"),
        st.Page("pages/Reports.py", title="Reports", icon="📊"),
    ],
    "Team modules": [
        st.Page("pages/Live_AI.py", title="Live AI Analysis", icon="🤖"),
        st.Page("pages/Settings.py", title="Settings", icon="⚙️"),
    ],
}
 
pg = st.navigation(pages)
pg.run()
 