"""
OCR Notes Page
--------------
Allows users to:

1. Upload an image.
2. Extract text using EasyOCR.
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
import easyocr
from PIL import Image

from utils.data_manager import (
    save_ocr_note,
    load_ocr_notes,
)


# NOTE:
# st.set_page_config() is NOT called here.
# app.py already calls it once for the whole multipage app.


# ===========================================================================
# Page header
# ===========================================================================

st.title("📝 OCR Notes")

st.write(
    "Upload an image, extract its text using OCR, "
    "and save the result as a note."
)


# ===========================================================================
# EasyOCR Reader
# ===========================================================================

@st.cache_resource
def get_ocr_reader(language):
    """
    Create and cache an EasyOCR reader.

    EasyOCR uses:
        en = English
        ar = Arabic

    For English + Arabic:
        ["en", "ar"]
    """

    if language == "eng":
        languages = ["en"]

    elif language == "ara":
        languages = ["ar"]

    elif language == "eng+ara":
        languages = ["en", "ar"]

    else:
        languages = ["en"]

    return easyocr.Reader(
        languages,
        gpu=False,
    )


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

        st.error(
            f"Could not open the uploaded image: {e}"
        )

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

        with st.spinner(
            "Loading OCR model and extracting text..."
        ):

            try:

                # -----------------------------------------------------------
                # Convert PIL image to RGB
                # -----------------------------------------------------------

                image_rgb = image.convert("RGB")


                # -----------------------------------------------------------
                # Get OCR reader
                # -----------------------------------------------------------

                reader = get_ocr_reader(language)


                # -----------------------------------------------------------
                # Run OCR
                # -----------------------------------------------------------

                results = reader.readtext(
                    image_rgb,
                    detail=0,
                    paragraph=True,
                )


                # -----------------------------------------------------------
                # Combine OCR results
                # -----------------------------------------------------------

                extracted_text = "\n".join(
                    str(text).strip()
                    for text in results
                    if str(text).strip()
                ).strip()


                # -----------------------------------------------------------
                # OCR result
                # -----------------------------------------------------------

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


            except Exception as e:

                st.error(
                    f"❌ OCR failed: {e}"
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
                    subject=cleaned_title or "OCR Note",

                    extracted_text=cleaned_text,
                )


                st.success(
                    "✅ OCR note saved successfully!"
                )


                # Clear current OCR text after saving
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

    if notes.empty:

        st.info(
            "No OCR notes saved yet."
        )


    # -----------------------------------------------------------------------
    # Display notes (most recent first)
    # -----------------------------------------------------------------------

    else:

        st.write(
            f"**{len(notes)} note(s) saved**"
        )


        for index, note in enumerate(
            notes.iloc[::-1].itertuples(),
            start=1,
        ):

            title = (
                getattr(
                    note,
                    "subject",
                    None,
                )
                or f"OCR Note {index}"
            )


            content = getattr(
                note,
                "extracted_text",
                "",
            )


            timestamp = getattr(
                note,
                "timestamp",
                "",
            )


            with st.expander(
                f"📝 {title} — {timestamp}",
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