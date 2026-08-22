import sys
from pathlib import Path

import streamlit as st


# ============================================================
# Project Path
# ============================================================

# app.py is located at:
# EduVision-main/src/dashboard/app.py
#
# parents[0] = dashboard
# parents[1] = src
# parents[2] = EduVision-main

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Make sure Python can find the "src" package
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
# Computer Vision Imports
# ============================================================
#
# The app now initializes ONE VisionPipeline (which wires together
# face recognition, object/distraction detection, hand detection, and
# attendance tracking) instead of separate detectors per page. Every
# page reads results from this same pipeline via st.session_state.

try:

    from src.computer_vision.vision_pipeline import VisionPipeline

    CV_IMPORT_ERROR = None

except Exception as e:

    VisionPipeline = None

    CV_IMPORT_ERROR = e


# ============================================================
# Initialize Computer Vision System
# ============================================================

@st.cache_resource
def initialize_vision_pipeline():

    if VisionPipeline is None:
        raise RuntimeError(
            "Computer Vision modules could not be imported."
        )

    return VisionPipeline()


# ============================================================
# Start Computer Vision
# ============================================================

try:

    vision_pipeline = initialize_vision_pipeline()

    st.session_state["vision_pipeline"] = vision_pipeline
    st.session_state["vision_initialized"] = True

    vision_error = None

except Exception as e:

    st.session_state["vision_pipeline"] = None
    st.session_state["vision_initialized"] = False

    vision_error = e


# ============================================================
# Pages
# ============================================================

# IMPORTANT:
# Because app.py is inside src/dashboard,
# the pages folder is simply "pages/..."

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

    st.caption(
        "Smart classroom monitoring & reporting"
    )

    st.divider()

    # --------------------------------------------------------
    # Computer Vision Status
    # --------------------------------------------------------

    st.subheader("Computer Vision")

    if st.session_state.get(
        "vision_initialized",
        False
    ):

        st.success(
            "Computer Vision Ready"
        )

        st.caption("Active modules:")

        st.write("✅ Face Recognition (multi-student)")
        st.write("✅ Object Detection")
        st.write("✅ Distraction Detection")
        st.write("✅ Hand Detection")
        st.write("✅ Attendance Tracking")

    else:

        st.error(
            "Computer Vision Unavailable"
        )

        if CV_IMPORT_ERROR is not None:

            st.caption(
                f"Import error: {CV_IMPORT_ERROR}"
            )

        elif vision_error is not None:

            st.caption(
                f"Initialization error: {vision_error}"
            )

        else:

            st.caption(
                "Some Computer Vision components "
                "could not be initialized."
            )

    st.divider()

    # --------------------------------------------------------
    # Team
    # --------------------------------------------------------

    st.subheader("Team")

    st.markdown(
        """
        **Malak Hossam**

        **Roqaya Mohamed**

        **Sara Elsayed**
        """
    )


# ============================================================
# Run Selected Page
# ============================================================

pg.run()
