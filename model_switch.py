import os
import fitz  # PyMuPDF
import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"

# Available models
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
st.set_page_config(
    page_title="Ollama Chat",
    page_icon="💬",
    layout="centered"
)
st.title("🤖 UmairAi - Local AI Chatbot")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = list(MODEL_OPTIONS.values())[0]
if "file_content" not in st.session_state:
    st.session_state.file_content = ""

# --- Model Selection ---
selected_label = st.selectbox("Choose a model:", list(MODEL_OPTIONS.keys()))
st.session_state.selected_model = MODEL_OPTIONS[selected_label]


# --- Chat History Display ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input + File Upload Like ChatGPT ---
user_input = st.chat_input("Ask something...")

uploaded_chat_file = st.file_uploader("📎 Attach a file", type=["py", "txt", "pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

# If file is uploaded via chat-style uploader
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

    # Store a message about file upload in history
    st.chat_message("user").markdown(file_info)
    st.session_state.chat_history.append({"role": "user", "content": file_info})

# If user types a message
if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Full prompt with history and file content
    full_prompt = build_prompt(
        history=st.session_state.chat_history,
        file_context=st.session_state.file_content
    )

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
    st.session_state.chat_history.append({"role": "assistant", "content": answer})


#  Clear Chat ---
if st.button("🗑️ Clear Chat History"):
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        st.session_state.clear()
    st.rerun()










































































# import streamlit as st
# import requests
# import base64
# import fitz  # PyMuPDF

# OLLAMA_URL = "http://localhost:11434/api/generate"

# # --- UI Setup ---
# st.set_page_config(page_title="Code Assistant", layout="wide")
# st.title("🧠 Local Code Assistant with Ollama")

# # --- Model Selection ---
# model_options = {
#     "TinyLLaMA": "tinyllama:latest",
#     "DeepSeek Coder": "deepseek-coder:1.3b"
# }
# model_label = st.selectbox("Select model to use:", options=list(model_options.keys()))
# MODEL_NAME = model_options[model_label]

# # --- File Upload ---
# uploaded_file = st.file_uploader("Upload a file (code, text, pdf, image)", type=["py", "txt", "pdf", "png", "jpg", "jpeg"])
# file_contents = ""

# if uploaded_file:
#     file_contents = uploaded_file.read()
#     st.success(f"Uploaded: {uploaded_file.name}")
    
#     if uploaded_file.type.startswith("text") or uploaded_file.name.endswith(".py"):
#         file_contents = file_contents.decode("utf-8")
#         st.code(file_contents[:1000], language="python")
#     elif uploaded_file.type.startswith("image"):
#         st.image(uploaded_file)
#     elif uploaded_file.name.endswith(".pdf"):
#         with open("temp_uploaded.pdf", "wb") as f:
#             f.write(file_contents)

#         doc = fitz.open("temp_uploaded.pdf")
#         pdf_text = ""
#         for page in doc:
#             pdf_text += page.get_text()
#         doc.close()

#         st.text_area("📄 PDF Content Extracted:", pdf_text[:3000], height=300)
#         file_contents = pdf_text

# # --- Chat Interface ---
# prompt = st.text_area("💬 Ask your coding question:", height=200)

# if st.button("🧠 Send to Ollama"):
#     full_prompt = prompt
#     if file_contents:
#         full_prompt += "\n\nHere is the file content:\n" + file_contents[:4000]

#     with st.spinner(f"Thinking with model: {MODEL_NAME}..."):
#         response = requests.post(OLLAMA_URL, json={
#             "model": MODEL_NAME,
#             "prompt": full_prompt,
#             "stream": False
#         })

#         if response.status_code == 200:
#             answer = response.json()["response"]
#             st.success("Ollama replied:")
#             st.code(answer)
#         else:
#             st.error("Failed to get a response from Ollama.")
