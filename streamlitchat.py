import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import speech_recognition as sr
from streamlit_chat import message

load_dotenv()  # Load environment variables from .env file (if any)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Error: GEMINI_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Or 'gemini-pro', or the model of your choice

def format_history(msg: str, history: list[list[str, str]], system_prompt: str):
    chat_history = [system_prompt]  # System Prompt
    for query, response in history:
        chat_history.append(f"User: {query}")
        chat_history.append(f"Assistant: {response}")
    chat_history.append(f"User: {msg}")
    return "\n".join(chat_history)  # Join as a single string for Gemini

def generate_response(msg: str, history: list[list[str, str]], system_prompt: str):
    formatted_prompt = format_history(msg, history, system_prompt)
    chat = model.start_chat(history=[])  # You can initialize with a system prompt too, as a role="user" message with the system prompt as content
    response = chat.send_message(formatted_prompt)  # Pass the entire formatted prompt

    message = ""
    for chunk in response:
        message += chunk.text
    return message

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    return ""

st.title("AI Chatbot")
st.write("Feel free to ask any question.")

system_prompt = st.text_area("System Prompt", """
you are an experienced advocate that knows about every policy and can easily
list down the errors by seeing the policies given by users. Be professional and 
polite to users while talking.
""")

if "history" not in st.session_state:
    st.session_state.history = []

# Add buttons for recording and pausing
if "recording" not in st.session_state:
    st.session_state.recording = False

if st.button("Record"):
    st.session_state.recording = True

if st.button("Pause"):
    st.session_state.recording = False

user_input = st.text_input("You:")

if st.session_state.recording:
    user_input = recognize_speech()

if user_input:
    st.session_state.history.append([user_input, ""])
    response = generate_response(user_input, st.session_state.history, system_prompt)
    st.session_state.history[-1][1] = response
    message(response, is_user=False)

for i, (query, response) in enumerate(st.session_state.history):
    message(query, is_user=True, key=f"user_{i}")
    message(response, is_user=False, key=f"assistant_{i}")
