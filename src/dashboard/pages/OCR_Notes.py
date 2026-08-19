"""
OCR Notes Page
--------------
Allows users to:

1. Upload an image.
2. Extract text using Tesseract OCR.
3. Review and edit the extracted text.
4. Save the OCR result as a note.
5. Display previously saved OCR notes.
"""

import sys
from pathlib import Path


# ===========================================================================
# Make src/ available for imports
# ===========================================================================

SRC_DIR = Path(__file__).resolve().parents[2]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ===========================================================================
# Imports
# ===========================================================================

import streamlit as st
import pytesseract
from PIL import Image

from utils.data_manager import (
    save_ocr_note,
    load_ocr_notes,
)


# ===========================================================================
# Page configuration
# ===========================================================================

st.set_page_config(
    page_title="OCR Notes",
    page_icon="📝",
    layout="wide",
)


# ===========================================================================
# Page header
# ===========================================================================

st.title("📝 OCR Notes")

st.write(
    "Upload an image, extract its text using OCR, "
    "and save the result as a note."
)


# ===========================================================================
# Check Tesseract
# ===========================================================================

def check_tesseract() -> bool:
    """Check whether Tesseract OCR is available."""

    try:
        pytesseract.get_tesseract_version()
        return True

    except Exception:
        return False


# ===========================================================================
# Image upload
# ===========================================================================

uploaded_file = st.file_uploader(
    "Upload an image",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp",
    ],
)


# ===========================================================================
# OCR section
# ===========================================================================

if uploaded_file is not None:

    # -----------------------------------------------------------------------
    # Open image
    # -----------------------------------------------------------------------

    try:
        image = Image.open(uploaded_file)

    except Exception as e:
        st.error(f"Could not open the uploaded image: {e}")
        st.stop()

    # -----------------------------------------------------------------------
    # Display image
    # -----------------------------------------------------------------------

    st.subheader("🖼️ Uploaded Image")

    st.image(
        image,
        use_container_width=True,
    )

    # -----------------------------------------------------------------------
    # OCR language
    # -----------------------------------------------------------------------

    st.subheader("🌐 OCR Settings")

    language = st.selectbox(
        "OCR Language",
        options=[
            "eng",
            "ara",
            "eng+ara",
        ],
        format_func=lambda lang: {
            "eng": "English",
            "ara": "Arabic",
            "eng+ara": "English + Arabic",
        }[lang],
        index=0,
    )

    # -----------------------------------------------------------------------
    # Extract button
    # -----------------------------------------------------------------------

    if st.button(
        "🔍 Extract Text",
        type="primary",
        use_container_width=True,
    ):

        # Check Tesseract installation
        if not check_tesseract():
            st.error(
                "Tesseract OCR is not installed or cannot be found. "
                "Please install Tesseract and make sure it is available "
                "in your PATH."
            )

        else:

            with st.spinner("Extracting text..."):

                try:

                    extracted_text = pytesseract.image_to_string(
                        image,
                        lang=language,
                    )

                    extracted_text = extracted_text.strip()

                    # -------------------------------------------------------
                    # OCR result
                    # -------------------------------------------------------

                    if extracted_text:

                        st.session_state["ocr_text"] = extracted_text

                        st.success(
                            "✅ Text extracted successfully!"
                        )

                    else:

                        st.session_state["ocr_text"] = ""

                        st.warning(
                            "⚠️ No text was detected in the image."
                        )

                except pytesseract.TesseractError as e:

                    st.error(
                        f"Tesseract OCR error: {e}"
                    )

                except Exception as e:

                    st.error(
                        f"OCR failed: {e}"
                    )


# ===========================================================================
# Display extracted text
# ===========================================================================

if (
    "ocr_text" in st.session_state
    and st.session_state["ocr_text"]
):

    st.divider()

    st.subheader("📄 Extracted Text")

    # -----------------------------------------------------------------------
    # Text editor
    # -----------------------------------------------------------------------

    edited_text = st.text_area(
        "Review or edit the extracted text",
        value=st.session_state["ocr_text"],
        height=300,
    )

    # Keep edited version in session state
    st.session_state["ocr_text"] = edited_text

    # -----------------------------------------------------------------------
    # Note title
    # -----------------------------------------------------------------------

    note_title = st.text_input(
        "Note title",
        value="OCR Note",
        placeholder="Enter a title for this note",
    )

    # -----------------------------------------------------------------------
    # Save note
    # -----------------------------------------------------------------------

    if st.button(
        "💾 Save Note",
        use_container_width=True,
    ):

        cleaned_text = edited_text.strip()
        cleaned_title = note_title.strip()

        if not cleaned_text:

            st.warning(
                "⚠️ There is no text to save."
            )

        else:

            try:

                save_ocr_note(
                    title=cleaned_title or "OCR Note",
                    content=cleaned_text,
                )

                st.success(
                    "✅ OCR note saved successfully!"
                )

                # Clear the current OCR text after saving
                st.session_state.pop(
                    "ocr_text",
                    None,
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Could not save note: {e}"
                )


# ===========================================================================
# Saved OCR notes
# ===========================================================================

st.divider()

st.subheader("📚 Saved OCR Notes")


try:

    notes = load_ocr_notes()

    # -----------------------------------------------------------------------
    # No notes
    # -----------------------------------------------------------------------

    if not notes:

        st.info(
            "No OCR notes saved yet."
        )

    # -----------------------------------------------------------------------
    # Display notes
    # -----------------------------------------------------------------------

    else:

        st.write(
            f"**{len(notes)} note(s) saved**"
        )

        for index, note in enumerate(
            reversed(notes),
            start=1,
        ):

            # ---------------------------------------------------------------
            # Handle dictionary notes
            # ---------------------------------------------------------------

            if isinstance(note, dict):

                title = note.get(
                    "title",
                    f"OCR Note {index}",
                )

                content = note.get(
                    "content",
                    note.get(
                        "text",
                        "",
                    ),
                )

            # ---------------------------------------------------------------
            # Handle unexpected note format
            # ---------------------------------------------------------------

            else:

                title = f"OCR Note {index}"
                content = str(note)

            # ---------------------------------------------------------------
            # Display note
            # ---------------------------------------------------------------

            with st.expander(
                f"📝 {title}",
                expanded=False,
            ):

                st.text_area(
                    "Note content",
                    value=str(content),
                    height=200,
                    key=f"saved_note_{index}",
                    disabled=True,
                )


except Exception as e:

    st.warning(
        f"⚠️ Could not load saved OCR notes: {e}"
    )