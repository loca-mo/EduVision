import sys
from pathlib import Path
import streamlit as st
from gtts import gTTS
import io
from streamlit_mic_recorder import speech_to_text
from google import genai
from google.genai import types
 
# Path setup
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
 
st.set_page_config(page_title="EduVision AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 Classroom AI & Voice Assistant")
st.caption("Ask questions, query student performance, or record voice commands.")
 
# --- GEMINI CLIENT SETUP ---
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
 
client = get_gemini_client()
 
SYSTEM_INSTRUCTION = (
    "You are EduVision AI, a classroom analytics assistant. "
    "Answer questions about attendance, student performance, and notes "
    "clearly and concisely for a teacher."
)
 
# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am EduVision AI. How can I help with your classroom analytics or notes today?"}
    ]
 
# Function to generate Text-to-Speech audio
def text_to_speech(text: str):
    tts = gTTS(text=text, lang="en")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp
 
# Function to call Gemini with full chat history
def get_ai_response(history: list) -> str:
    # Gemini uses "model" instead of "assistant" as the role name
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in history
    ]
 
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            max_output_tokens=500,
        ),
    )
    return response.text
 
# --- VOICE INPUT SECTION ---
st.subheader("🎙️ Voice Input")
voice_text = speech_to_text(
    language='en',
    start_prompt="Click to Speak 🎙️",
    stop_prompt="Stop Recording ⏹️",
    key='voice_input'
)
 
# --- DISPLAY CHAT HISTORY ---
st.subheader("💬 Chat")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
 
# Process input (Text or Voice)
user_query = st.chat_input("Type your question here...") or voice_text
 
if user_query:
    # 1. Store and render user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
 
    # 2. Real Gemini API call
    with st.spinner("Thinking..."):
        try:
            response_text = get_ai_response(st.session_state.messages)
        except Exception as e:
            response_text = f"Sorry, I ran into an error talking to Gemini: {e}"
 
    # 3. Store and render assistant message
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.write(response_text)
 
        # Play voice response
        audio_fp = text_to_speech(response_text)
        st.audio(audio_fp, format="audio/mp3", autoplay=True)
 