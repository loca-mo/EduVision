import io
from typing import Dict, List, Optional

import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from google import genai
from google.genai import types


# ============================================================
# PAGE / APP CONFIG
# ============================================================
# NOTE: st.set_page_config() is intentionally not called here
# because app.py already calls it for the multipage application.

MODEL_NAME = "gemini-3.6-flash"
MAX_HISTORY_MESSAGES = 20
MAX_OUTPUT_TOKENS = 900
TEMPERATURE = 0.35

SYSTEM_INSTRUCTION = """
You are EduVision AI, an intelligent classroom assistant for teachers.

Your responsibilities include:
- Student attendance
- Student performance
- Classroom analytics
- Notes and OCR content
- Learning support
- Student progress
- Reports
- Educational questions

Response rules:
1. Be clear, concise, professional, and practical.
2. Use the classroom data supplied in the conversation when it is available.
3. Never invent student names, grades, attendance values, statistics, or events.
4. If required information is missing, explicitly say what is missing.
5. When numbers are provided, reason from those numbers and explain important results simply.
6. Separate observed facts from recommendations.
7. Protect student privacy. Do not expose unnecessary personal information.
8. Do not diagnose medical, psychological, or learning disorders. If a concern is mentioned,
   recommend appropriate teacher/school support instead.
9. When comparing students or groups, use a compact table when useful.
10. For recommendations, give concrete actions a teacher can take.
11. If asked to summarize, prefer headings and bullet points.
12. If the question is unrelated to education, answer briefly and helpfully.
13. Never claim to have uploaded, saved, analyzed, or performed an action unless it actually happened.
14. If the available data is insufficient to make a reliable conclusion, say so.
"""


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource(show_spinner=False)
def get_gemini_client():
    """Create and cache the Gemini client using Streamlit secrets."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error(
            "GEMINI_API_KEY was not found. Add it to "
            ".streamlit/secrets.toml before using EduVision AI."
        )
        st.stop()

    if not api_key or not str(api_key).strip():
        st.error("GEMINI_API_KEY is empty. Please check your Streamlit secrets.")
        st.stop()

    return genai.Client(api_key=api_key)


client = get_gemini_client()


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hello! I’m EduVision AI.**\n\n"
                    "I can help you understand classroom data, attendance, "
                    "performance, notes, progress, and reports.\n\n"
                    "Ask me a question below to get started."
                ),
            }
        ]

    if "last_response_audio" not in st.session_state:
        st.session_state.last_response_audio = None

    if "last_response_text" not in st.session_state:
        st.session_state.last_response_text = ""


initialize_state()


# ============================================================
# HELPERS
# ============================================================

def trim_history(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Keep the prompt reasonably small while preserving the welcome message."""
    if len(messages) <= MAX_HISTORY_MESSAGES + 1:
        return messages

    first = messages[:1]
    recent = messages[-MAX_HISTORY_MESSAGES:]
    return first + recent


def build_gemini_history(messages: List[Dict[str, str]]) -> List[types.Content]:
    """Convert Streamlit messages into Gemini Content objects."""
    contents: List[types.Content] = []

    for message in trim_history(messages):
        role = message.get("role", "")
        content = str(message.get("content", "")).strip()

        if not content:
            continue

        if role == "assistant":
            role = "model"
        elif role != "user":
            continue

        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=content)],
            )
        )

    return contents


def get_ai_response(messages: List[Dict[str, str]]) -> str:
    """Send the current conversation to Gemini and return clean text."""
    history = build_gemini_history(messages)

    if not history:
        return "Please enter a classroom-related question."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=TEMPERATURE,
        ),
    )

    text = getattr(response, "text", None)
    if not text or not text.strip():
        return "I couldn't generate a response right now. Please try again."

    return text.strip()


@st.cache_data(show_spinner=False, max_entries=30)
def text_to_speech(text: str, language: str = "en") -> Optional[bytes]:
    """Convert response text to MP3 bytes and cache repeated requests."""
    if not text.strip():
        return None

    try:
        # Keep extremely long responses from creating oversized audio requests.
        spoken_text = text[:4000]
        tts = gTTS(text=spoken_text, lang=language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        return audio_buffer.getvalue()
    except Exception as error:
        print(f"TTS error: {error}")
        return None


def clear_chat() -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Chat cleared.**\n\n"
                "What would you like to analyze in your classroom?"
            ),
        }
    ]
    st.session_state.last_response_audio = None
    st.session_state.last_response_text = ""


def submit_question(question: str) -> None:
    """Put a suggested question into the pending input state."""
    question = question.strip()
    if question:
        st.session_state.pending_question = question


# ============================================================
# HEADER
# ============================================================

st.title("🤖 EduVision AI Assistant")
st.caption(
    "Your intelligent classroom assistant for attendance, performance, "
    "notes, reports, and educational analytics."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ AI Assistant")
    st.write("Ask EduVision AI using text or your voice.")

    st.divider()
    st.subheader("💡 Quick Questions")

    example_questions = [
        "How can I improve student attendance?",
        "How should I identify students who need support?",
        "Summarize the classroom performance data.",
        "What are effective ways to track student progress?",
        "How can I use my notes for revision?",
    ]

    for index, question in enumerate(example_questions):
        if st.button(
            question,
            key=f"example_question_{index}",
            use_container_width=True,
        ):
            submit_question(question)
            st.rerun()

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat()
        st.rerun()

    st.divider()
    st.caption("🔐 Gemini API key is loaded from Streamlit secrets.")
    st.caption(f"🧠 Model: {MODEL_NAME}")


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

if voice_text:
    st.info(f"Voice question: {voice_text}")


# ============================================================
# CHAT HISTORY
# ============================================================

st.subheader("💬 Chat")

for message in st.session_state.messages:
    role = message.get("role", "assistant")
    content = message.get("content", "")

    with st.chat_message(role):
        st.markdown(content)


# ============================================================
# INPUT
# ============================================================

pending_question = st.session_state.pop("pending_question", "")
text_input = st.chat_input("Ask EduVision AI something...")

# Typed input wins if both are available.
user_query = text_input or voice_text or pending_question


# ============================================================
# PROCESS QUERY
# ============================================================

if user_query:
    user_query = user_query.strip()

    if not user_query:
        st.warning("Please enter a question.")
        st.stop()

    # Prevent accidental processing of an identical query if the page is rerun.
    last_message = st.session_state.messages[-1] if st.session_state.messages else {}
    if last_message.get("role") == "user" and last_message.get("content") == user_query:
        st.stop()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("🤔 EduVision AI is thinking..."):
            try:
                response_text = get_ai_response(st.session_state.messages)
            except Exception as error:
                # Keep technical details out of the UI.
                print(f"Gemini API error: {error}")
                response_text = (
                    "⚠️ **I couldn't connect to the AI service.**\n\n"
                    "Please check your Gemini API key, internet connection, "
                    "and API configuration, then try again."
                )

        st.markdown(response_text)

        st.session_state.last_response_text = response_text
        st.session_state.last_response_audio = None

        # Generate audio only when requested instead of making a TTS network
        # request after every AI response.
        if st.button("🔊 Read this answer aloud", key="read_latest_answer"):
            with st.spinner("Generating audio..."):
                audio_bytes = text_to_speech(response_text)

            if audio_bytes:
                st.session_state.last_response_audio = audio_bytes
            else:
                st.warning("I couldn't generate audio for this answer.")

        if st.session_state.last_response_audio:
            st.audio(
                st.session_state.last_response_audio,
                format="audio/mp3",
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_text,
        }
    )
