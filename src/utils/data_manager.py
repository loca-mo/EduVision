import os
import pandas as pd
from datetime import datetime
 
# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
 
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.csv")
EVENTS_FILE = os.path.join(DATA_DIR, "events.csv")
OCR_NOTES_FILE = os.path.join(DATA_DIR, "ocr_notes.csv")
 
ATTENDANCE_COLUMNS = ["student_id", "student_name", "date", "status", "subject"]
EVENTS_COLUMNS = ["timestamp", "event_type", "source_module", "details"]
OCR_NOTES_COLUMNS = ["timestamp", "subject", "extracted_text", "image_ref"]
 
 
def _ensure_file(path: str, columns: list):
    """Create the file with the correct columns if it doesn't exist yet."""
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)
 
 
def _load(path: str, columns: list) -> pd.DataFrame:
    _ensure_file(path, columns)
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)
 
 
# ---------------------------------------------------------------------------
# Attendance (reads data from the teammate's attendance module, or add
# records manually here in the meantime)
# ---------------------------------------------------------------------------
def load_attendance() -> pd.DataFrame:
    return _load(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
 
 
def add_attendance_record(student_id, student_name, status, subject, date=None):
    df = load_attendance()
    new_row = {
        "student_id": student_id,
        "student_name": student_name,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "status": status,
        "subject": subject,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(ATTENDANCE_FILE, index=False)
    return df
 
 
# ---------------------------------------------------------------------------
# Events (written by different modules: hand-raise detection, entry/exit,
# alerts from the attendance module, etc.)
# ---------------------------------------------------------------------------
def load_events() -> pd.DataFrame:
    return _load(EVENTS_FILE, EVENTS_COLUMNS)
 
 
def log_event(event_type: str, source_module: str, details: str = ""):
    """Any module on the team can call this to log a new event."""
    df = load_events()
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "source_module": source_module,
        "details": details,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(EVENTS_FILE, index=False)
    return df
 
 
# ---------------------------------------------------------------------------
# OCR notes (blackboard)
# ---------------------------------------------------------------------------
def load_ocr_notes() -> pd.DataFrame:
    return _load(OCR_NOTES_FILE, OCR_NOTES_COLUMNS)
 
 
def save_ocr_note(subject: str, extracted_text: str, image_ref: str = ""):
    df = load_ocr_notes()
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subject": subject,
        "extracted_text": extracted_text,
        "image_ref": image_ref,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(OCR_NOTES_FILE, index=False)
    return df
 