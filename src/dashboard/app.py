import streamlit as st

from src.computer_vision.object_detection import ObjectDetector
from src.computer_vision.distraction_detection import DistractionDetector
from src.computer_vision.hand_detection import HandDetector


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="EduVision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Initialize Computer Vision Components
# ============================================================

@st.cache_resource
def initialize_vision_system():
    """
    Initialize all Computer Vision components once.

    The initialized components are cached by Streamlit so they
    are not recreated every time the application reruns.
    """

    object_detector = ObjectDetector()
    distraction_detector = DistractionDetector()
    hand_detector = HandDetector()

    return {
        "object_detector": object_detector,
        "distraction_detector": distraction_detector,
        "hand_detector": hand_detector,
    }


# Initialize the CV system safely.
# This prevents the whole dashboard from crashing if one
# Computer Vision dependency is unavailable.
try:
    vision_system = initialize_vision_system()

    st.session_state["vision_system"] = vision_system
    st.session_state["vision_initialized"] = True

except Exception as e:
    st.session_state["vision_system"] = None
    st.session_state["vision_initialized"] = False

    # Show the error only in the sidebar instead of crashing
    # the complete dashboard.
    with st.sidebar:
        st.warning("Computer Vision system is not fully available.")
        st.caption(str(e))


# ============================================================
# Pages
# ============================================================

dashboard_page = st.Page(
    "pages/Dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True,
)

attendance_page = st.Page(
    "pages/Attendance.py",
    title="Attendance",
    icon="🧍",
)

interaction_page = st.Page(
    "pages/Interaction.py",
    title="Interaction",
    icon="💬",
)

live_ai_page = st.Page(
    "pages/Live_AI.py",
    title="Live AI",
    icon="🎥",
)

ocr_notes_page = st.Page(
    "pages/OCR_Notes.py",
    title="OCR Notes",
    icon="📝",
)

ai_assistant_page = st.Page(
    "pages/AI_Assistant.py",
    title="AI & Voice Assistant",
    icon="🤖",
)

reports_page = st.Page(
    "pages/Reports.py",
    title="Reports",
    icon="📄",
)

settings_page = st.Page(
    "pages/Settings.py",
    title="Settings",
    icon="⚙️",
)


# ============================================================
# Navigation
# ============================================================

pg = st.navigation(
    {
        "Overview": [
            dashboard_page,
        ],
        "Classroom": [
            attendance_page,
            interaction_page,
            live_ai_page,
            ocr_notes_page,
            ai_assistant_page,
        ],
        "Insights": [
            reports_page,
        ],
        "App": [
            settings_page,
        ],
    }
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("🎓 EduVision")
    st.caption("Smart classroom monitoring & reporting")

    st.divider()

    st.subheader("Computer Vision")

    if st.session_state.get("vision_initialized", False):
        st.success("Computer Vision Ready")

        st.caption("Active modules:")

        st.write("✅ Object Detection")
        st.write("✅ Distraction Detection")
        st.write("✅ Hand Detection")

    else:
        st.error("Computer Vision Unavailable")
        st.caption(
            "Some Computer Vision components could not be initialized."
        )

    st.divider()

    st.subheader("Team")

    st.markdown(
        """
        Malak Hossam  
        Roqaya Mohamed  
        Sara Elsayed
        """
    )


# ============================================================
# Run Selected Page
# ============================================================
