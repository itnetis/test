import os
import fitz  # PyMuPDF
import requests
import streamlit as st
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_OPTIONS = {
    "TinyLLaMA": "tinyllama:latest",
    "DeepSeek Coder": "deepseek-coder:1.3b"
}

# --- Helper function to build prompt from history ---
def build_prompt(history, file_context=""):
    prompt = ""
    for msg in history:
        if msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        else:
            prompt += f"Assistant: {msg['content']}\n"
    if file_context:
        prompt += f"\nHere is the uploaded file content (if applicable):\n{file_context[:4000]}\n"
    prompt += "Assistant:"
    return prompt

# --- Streamlit Config ---
st.set_page_config(page_title="Umair Chat", page_icon="💬", layout="wide")
st.title("🤖 UmairAi - Local Chatbot")

# --- Initialize Session State ---
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = list(MODEL_OPTIONS.values())[0]
if "file_content" not in st.session_state:
    st.session_state.file_content = ""

# --- Sidebar: Chat Sessions ---
st.sidebar.header("💬 Your Chats")

# Display all chat titles in list
for chat_id, chat_data in st.session_state.chats.items():
    if st.sidebar.button(chat_data["title"], key=chat_id):
        st.session_state.active_chat = chat_id

# Button to start a new chat
if st.sidebar.button("➕ New Chat"):
    new_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = {
        "title": f"Chat {len(st.session_state.chats) + 1}",
        "history": []
    }
    st.session_state.active_chat = new_id
    st.session_state.file_content = ""

# --- Main Chat Area ---
if st.session_state.active_chat:
    chat_data = st.session_state.chats[st.session_state.active_chat]
    chat_history = chat_data["history"]

    # Model Selection
    selected_label = st.selectbox("Choose a model:", list(MODEL_OPTIONS.keys()))
    st.session_state.selected_model = MODEL_OPTIONS[selected_label]

    # Display chat history
    for msg in chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # File Upload like ChatGPT
    uploaded_chat_file = st.file_uploader("📎 Attach a file", type=["py", "txt", "pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_chat_file:
        raw_data = uploaded_chat_file.read()
        file_info = f"**Attached file:** `{uploaded_chat_file.name}`\n\n"

        if uploaded_chat_file.type.startswith("text") or uploaded_chat_file.name.endswith(".py"):
            text = raw_data.decode("utf-8")
            st.session_state.file_content = text
            file_info += "```\n" + text[:1000] + "\n```"
        elif uploaded_chat_file.type.startswith("image"):
            st.image(uploaded_chat_file, caption=uploaded_chat_file.name)
            st.session_state.file_content = "[Image uploaded]"
            file_info += "_Image uploaded successfully._"
        elif uploaded_chat_file.name.endswith(".pdf"):
            with open("temp_chat.pdf", "wb") as f:
                f.write(raw_data)
            doc = fitz.open("temp_chat.pdf")
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text()
            doc.close()
            st.session_state.file_content = pdf_text
            file_info += f"📄 **Extracted from PDF:**\n\n{pdf_text[:1000]}"

        # Add file info to history
        chat_history.append({"role": "user", "content": file_info})
        st.chat_message("user").markdown(file_info)

    # Chat input
    user_input = st.chat_input("Ask something...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        chat_history.append({"role": "user", "content": user_input})

        full_prompt = build_prompt(chat_history, file_context=st.session_state.file_content)

        with st.spinner(f"Thinking with {st.session_state.selected_model}..."):
            response = requests.post(OLLAMA_URL, json={
                "model": st.session_state.selected_model,
                "prompt": full_prompt,
                "stream": False
            })
            if response.status_code == 200:
                answer = response.json().get("response", "").strip()
            else:
                answer = "⚠️ Error: Could not get a response from Ollama."

        st.chat_message("assistant").markdown(answer)
        chat_history.append({"role": "assistant", "content": answer})

    # Clear chat button
    if st.button("🗑️ Clear This Chat"):
        chat_data["history"] = []
        st.session_state.file_content = ""
        st.experimental_rerun()
else:
    st.info("Start a new chat from the sidebar or select an existing one.")
