"""
OCR_Notes.py
-------------
OCR notes page: allows users to upload an image,
extract text using Tesseract OCR, save the result,
and display previously saved OCR notes.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make src/ available so imports like `from utils.data_manager ...` work
# ---------------------------------------------------------------------------
SRC_DIR = Path(__file__).resolve().parents[2]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import streamlit as st
import pytesseract
from PIL import Image

from utils.data_manager import save_ocr_note, load_ocr_notes


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OCR Notes",
    page_icon="📝",
    layout="wide",
)

st.title("📝 OCR Notes")
st.write("Upload an image and extract its text using OCR.")


# ---------------------------------------------------------------------------
# Image upload
# ---------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg", "webp"],
)


if uploaded_file is not None:

    # Open image
    image = Image.open(uploaded_file)

    # Display image
    st.subheader("Uploaded Image")
    st.image(image, use_container_width=True)

    # -----------------------------------------------------------------------
    # OCR language
    # -----------------------------------------------------------------------
    language = st.selectbox(
        "OCR Language",
        options=["eng", "ara", "eng+ara"],
        index=0,
    )

    # -----------------------------------------------------------------------
    # Extract text
    # -----------------------------------------------------------------------
    if st.button("🔍 Extract Text", type="primary"):

        with st.spinner("Extracting text..."):

            try:
                extracted_text = pytesseract.image_to_string(
                    image,
                    lang=language,
                )

                extracted_text = extracted_text.strip()

                if extracted_text:
                    st.session_state["ocr_text"] = extracted_text
                    st.success("Text extracted successfully!")

                else:
                    st.session_state["ocr_text"] = ""
                    st.warning(
                        "No text was detected in the image."
                    )

            except Exception as e:
                st.error(f"OCR failed: {e}")


# ---------------------------------------------------------------------------
# Display extracted text
# ---------------------------------------------------------------------------
if "ocr_text" in st.session_state and st.session_state["ocr_text"]:

    st.subheader("📄 Extracted Text")

    edited_text = st.text_area(
        "Review or edit the extracted text",
        value=st.session_state["ocr_text"],
        height=300,
    )

    # -----------------------------------------------------------------------
    # Save OCR note
    # -----------------------------------------------------------------------
    note_title = st.text_input(
        "Note title",
        value="OCR Note",
    )

    if st.button("💾 Save Note"):

        if edited_text.strip():

            try:
                save_ocr_note(
                    title=note_title.strip() or "OCR Note",
                    content=edited_text.strip(),
                )

                st.success("OCR note saved successfully!")

            except TypeError:
                # Fallback in case data_manager uses a different signature
                try:
                    save_ocr_note(
                        edited_text.strip()
                    )

                    st.success("OCR note saved successfully!")

                except Exception as e:
                    st.error(f"Could not save note: {e}")

            except Exception as e:
                st.error(f"Could not save note: {e}")

        else:
            st.warning("There is no text to save.")


# ---------------------------------------------------------------------------
# Previously saved OCR notes
# ---------------------------------------------------------------------------
st.divider()

st.subheader("📚 Saved OCR Notes")

try:
    notes = load_ocr_notes()

    if notes is None or len(notes) == 0:
        st.info("No OCR notes saved yet.")

    else:

        # Handle DataFrame results
        if hasattr(notes, "iterrows"):

            for _, note in notes.iterrows():

                title = note.get("title", "OCR Note")
                content = note.get("content", "")

                with st.expander(str(title)):

                    st.write(str(content))

        # Handle list results
        elif isinstance(notes, list):

            for i, note in enumerate(notes):

                if isinstance(note, dict):

                    title = note.get(
                        "title",
                        f"OCR Note {i + 1}",
                    )

                    content = note.get(
                        "content",
                        note.get("text", ""),
                    )

                else:

                    title = f"OCR Note {i + 1}"
                    content = str(note)

                with st.expander(str(title)):

                    st.write(str(content))

        else:
            st.write(notes)

except Exception as e:
    st.warning(f"Could not load saved OCR notes: {e}")