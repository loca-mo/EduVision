import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.data_manager import load_events

st.title("✋ Classroom Interaction")
st.caption("Monitoring Hand Raises, Participation, and Activity")

pipeline = st.session_state.get("vision_pipeline")
result = pipeline.last_result if pipeline else None

col1, col2 = st.columns(2)

with col1:
    hand_count = result["raised_hands"] if result else 0
    st.metric("Raised Hands (current frame)", hand_count)

with col2:
    distraction_count = result["distraction_count"] if result else 0
    st.metric("Distractions (current frame)", distraction_count)

st.caption(
    "These update live while the **Live AI** page has the camera running — "
    "this page reads from the same shared pipeline, it doesn't open its own camera."
)

st.divider()

st.subheader("📋 Recent Events")

events = load_events()

if events.empty:
    st.info("No events logged yet.")
else:
    st.dataframe(
        events.sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
