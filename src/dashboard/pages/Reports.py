"""
Reports.py
----------
Reports dashboard displaying attendance, events, and OCR notes.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Fix imports
# ---------------------------------------------------------------------------
# Reports.py is located at:
# src/dashboard/pages/Reports.py
#
# parents[0] -> pages
# parents[1] -> dashboard
# parents[2] -> src
#
# This allows:
# from utils.data_manager import ...
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).resolve().parents[2]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_manager import (
    load_attendance,
    load_events,
    load_ocr_notes,
)


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Reports",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Reports")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

try:
    attendance = load_attendance()
except Exception as e:
    attendance = pd.DataFrame()
    st.warning(f"Could not load attendance data: {e}")


try:
    events = load_events()
except Exception as e:
    events = pd.DataFrame()
    st.warning(f"Could not load events data: {e}")


try:
    ocr_notes = load_ocr_notes()
except Exception as e:
    ocr_notes = pd.DataFrame()
    st.warning(f"Could not load OCR notes: {e}")


# ---------------------------------------------------------------------------
# Convert returned data to DataFrames where necessary
# ---------------------------------------------------------------------------

if attendance is None:
    attendance = pd.DataFrame()

if events is None:
    events = pd.DataFrame()

if ocr_notes is None:
    ocr_notes = pd.DataFrame()


# If a loader returns a list of dictionaries, convert it to DataFrame
if isinstance(attendance, list):
    attendance = pd.DataFrame(attendance)

if isinstance(events, list):
    events = pd.DataFrame(events)

if isinstance(ocr_notes, list):
    ocr_notes = pd.DataFrame(ocr_notes)


# ---------------------------------------------------------------------------
# Overview metrics
# ---------------------------------------------------------------------------

attendance_records = len(attendance)
event_count = len(events)
ocr_note_count = len(ocr_notes)

attendance_rate = 0.0

if not attendance.empty and "status" in attendance.columns:
    total_attendance = len(attendance)

    present_count = (
        attendance["status"]
        .astype(str)
        .str.lower()
        .eq("present")
        .sum()
    )

    if total_attendance > 0:
        attendance_rate = (
            present_count / total_attendance
        ) * 100


m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Attendance Records",
    attendance_records,
)

m2.metric(
    "Attendance Rate",
    f"{attendance_rate:.1f}%",
)

m3.metric(
    "Events",
    event_count,
)

m4.metric(
    "OCR Notes",
    ocr_note_count,
)


# ---------------------------------------------------------------------------
# Attendance Report
# ---------------------------------------------------------------------------

st.divider()

st.subheader("✅ Attendance Report")

if attendance.empty:

    st.info("No attendance data available.")

else:

    attendance_display = attendance.copy()

    # Convert date column if available
    if "date" in attendance_display.columns:
        attendance_display["date"] = pd.to_datetime(
            attendance_display["date"],
            errors="coerce",
        )

    # ---------------------------------------------------------------
    # Attendance chart
    # ---------------------------------------------------------------

    if (
        "date" in attendance_display.columns
        and "status" in attendance_display.columns
    ):

        attendance_chart = (
            attendance_display
            .assign(
                date=attendance_display["date"].dt.date,
                status=attendance_display["status"]
                .astype(str)
                .str.lower(),
            )
            .groupby(["date", "status"])
            .size()
            .reset_index(name="count")
        )

        if not attendance_chart.empty:

            fig = px.bar(
                attendance_chart,
                x="date",
                y="count",
                color="status",
                barmode="group",
                title="Attendance by Day",
                labels={
                    "date": "Date",
                    "count": "Number of Records",
                    "status": "Status",
                },
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    # ---------------------------------------------------------------
    # Attendance table
    # ---------------------------------------------------------------

    st.dataframe(
        attendance_display.sort_values(
            "date",
            ascending=False,
        )
        if "date" in attendance_display.columns
        else attendance_display,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# Events Report
# ---------------------------------------------------------------------------

st.divider()

st.subheader("📅 Events")

if events.empty:

    st.info("No events available.")

else:

    events_display = events.copy()

    # Convert possible date columns
    for column in ["date", "event_date", "start_date"]:
        if column in events_display.columns:
            events_display[column] = pd.to_datetime(
                events_display[column],
                errors="coerce",
            )

    st.dataframe(
        events_display,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# OCR Notes Report
# ---------------------------------------------------------------------------

st.divider()

st.subheader("📝 OCR Notes")

if ocr_notes.empty:

    st.info("No OCR notes available.")

else:

    # ---------------------------------------------------------------
    # Display OCR notes
    # ---------------------------------------------------------------

    if (
        "title" in ocr_notes.columns
        or "content" in ocr_notes.columns
        or "text" in ocr_notes.columns
    ):

        for index, note in ocr_notes.iterrows():

            title = note.get(
                "title",
                f"OCR Note {index + 1}",
            )

            content = note.get(
                "content",
                note.get("text", ""),
            )

            with st.expander(str(title)):

                st.write(str(content))

    else:

        st.dataframe(
            ocr_notes,
            use_container_width=True,
            hide_index=True,
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

st.divider()

st.subheader("📌 Report Summary")

summary_data = {
    "Metric": [
        "Attendance Records",
        "Attendance Rate",
        "Events",
        "OCR Notes",
    ],
    "Value": [
        attendance_records,
        f"{attendance_rate:.1f}%",
        event_count,
        ocr_note_count,
    ],
}

summary_df = pd.DataFrame(summary_data)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)