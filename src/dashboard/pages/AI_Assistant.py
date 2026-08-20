import io
from pathlib import Path

import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EduVision AI Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# CONSTANTS
# ============================================================

MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """
You are EduVision AI, an intelligent classroom analytics assistant.

Your job is to help teachers with:
- Student attendance
- Student performance
- Classroom analytics
- Notes and OCR content
- Learning difficulties
- Student progress
- Reports
- General educational questions

Rules:
1. Be clear, concise, and professional.
2. Give practical answers that are useful to teachers.
3. If the teacher asks about student data that has not been provided,
   clearly say that you do not have access to that data.
4. Never invent student names, grades, attendance percentages,
   or other classroom statistics.
5. When analyzing numbers, explain the result simply.
6. Protect student privacy.
7. If asked to summarize something, use bullet points when appropriate.
8. If the question is unrelated to education/classroom analytics,
   you can still answer helpfully, but keep the response concise.
9. Do not claim that you performed an action if you did not actually
   perform it.
"""


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_gemini_client():
    """
    Create and cache the Gemini client.

    The API key is loaded from:
    .streamlit/secrets.toml
    """

    if "GEMINI_API_KEY" not in st.secrets:
        st.error(
            "GEMINI_API_KEY was not found in Streamlit secrets."
        )
        st.stop()

    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello! I am EduVision AI. "
                "I can help you analyze classroom information, "
                "attendance, performance, notes, and reports. "
                "How can I help?"
            ),
        }
    ]


# ============================================================
# TEXT TO SPEECH
# ============================================================

def text_to_speech(text: str):
    """
    Convert AI response text into MP3 audio.
    """

    try:
        tts = gTTS(
            text=text,
            lang="en",
            slow=False,
        )

        audio_buffer = io.BytesIO()

        tts.write_to_fp(audio_buffer)

        audio_buffer.seek(0)

        return audio_buffer

    except Exception:
        return None


# ============================================================
# BUILD GEMINI HISTORY
# ============================================================

def build_gemini_history(messages):
    """
    Convert Streamlit chat history into Gemini Content objects.
    """

    contents = []

    for message in messages:

        role = message["role"]

        # Gemini uses "model" instead of "assistant"
        if role == "assistant":
            role = "model"

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(
                        text=message["content"]
                    )
                ],
            )
        )

    return contents


# ============================================================
# GEMINI RESPONSE
# ============================================================

def get_ai_response(messages):
    """
    Send the conversation to Gemini and return the response.
    """

    history = build_gemini_history(messages)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=700,
            temperature=0.4,
        ),
    )

    if not response.text:
        return (
            "I couldn't generate a response right now. "
            "Please try again."
        )

    return response.text.strip()


# ============================================================
# HEADER
# ============================================================

st.title("🤖 EduVision AI Assistant")

st.caption(
    "Your classroom assistant for attendance, performance, "
    "notes, reports, and educational analytics."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ AI Assistant")

    st.write(
        "Ask EduVision AI questions using text or your voice."
    )

    st.divider()

    st.subheader("💡 Example Questions")

    example_questions = [
        "How can I improve student attendance?",
        "How should I identify students who need support?",
        "Summarize today's classroom performance.",
        "What are effective ways to track student progress?",
        "How can I use OCR notes for revision?",
    ]

    for question in example_questions:
        st.caption(f"• {question}")

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Chat cleared. "
                    "How can I help with your classroom?"
                ),
            }
        ]

        st.rerun()

    st.divider()

    st.caption(
        "🔐 Gemini API key is loaded securely from "
        "Streamlit secrets."
    )


# ============================================================
# VOICE INPUT
# ============================================================

st.subheader("🎙️ Voice Input")

voice_text = speech_to_text(
    language="en",
    start_prompt="🎙️ Click to Speak",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    use_container_width=True,
    key="voice_input",
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

st.subheader("💬 Chat")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# USER INPUT
# ============================================================

text_input = st.chat_input(
    "Ask EduVision AI something..."
)

# Prefer typed input if both happen at the same time
user_query = text_input or voice_text


# ============================================================
# PROCESS USER QUERY
# ============================================================

if user_query:

    user_query = user_query.strip()

    if not user_query:
        st.warning("Please enter a question.")
        st.stop()


    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )


    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_query)


    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🤔 EduVision AI is thinking..."):

            try:

                response_text = get_ai_response(
                    st.session_state.messages
                )

            except Exception as error:

                # Print the technical error in the terminal
                # during development, but don't expose it to users.
                print(
                    f"Gemini API error: {error}"
                )

                response_text = (
                    "⚠️ I couldn't connect to the AI service "
                    "right now.\n\n"
                    "Please check your Gemini API key, "
                    "internet connection, and API configuration."
                )


        # ----------------------------------------------------
        # DISPLAY RESPONSE
        # ----------------------------------------------------

        st.markdown(response_text)


        # ----------------------------------------------------
        # TEXT TO SPEECH
        # ----------------------------------------------------

        audio = text_to_speech(response_text)

        if audio is not None:

            st.audio(
                audio,
                format="audio/mp3",
                autoplay=True,
            )


    # --------------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_text,
        }
    )