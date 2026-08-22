import sys
from pathlib import Path
import streamlit as st

# Ensure Python can locate the 'src' folder for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.data_manager import load_attendance

st.title("👥 Attendance Tracking")

pipeline = st.session_state.get("vision_pipeline")
result = pipeline.last_result if pipeline else None

# ------------------------------------------------------------
# Live status (from the shared VisionPipeline / Live AI page)
# ------------------------------------------------------------

if result:
    live_col1, live_col2 = st.columns(2)

    with live_col1:
        st.metric("Currently Present (live)", len(result["present_ids"]))

    with live_col2:
        st.metric("Faces in Last Frame", result["people_count"])

    if result["present_ids"]:
        st.caption("Present now: " + ", ".join(result["present_ids"]))

else:
    st.info(
        "No live camera data yet — open the **Live AI** page and start "
        "the camera to begin taking attendance automatically."
    )

st.divider()

# ------------------------------------------------------------
# Attendance log (written by the pipeline as students check in)
# ------------------------------------------------------------

st.subheader("📋 Attendance Log")

df = load_attendance()
st.dataframe(df, use_container_width=True)
