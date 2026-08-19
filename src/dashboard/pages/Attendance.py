import sys
from pathlib import Path
import streamlit as st

# Ensure Python can locate the 'src' folder for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from utils.data_manager import load_attendance

st.title("👥 Attendance Tracking")

# Load and render data
df = load_attendance()
st.dataframe(df, use_container_width=True)