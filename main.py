import streamlit as st
import requests
import base64
import fitz  # PyMuPDF

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama:latest"
# MODEL_NAME = "deepseek-coder:1.3b"

st.set_page_config(page_title="Code Assistant", layout="wide")
st.title("🧠 Local Code Assistant with Ollama")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a file (code, text, pdf, image)", type=["py", "txt", "pdf", "png", "jpg", "jpeg"])
file_contents = ""

if uploaded_file:
    file_contents = uploaded_file.read()
    st.success(f"Uploaded: {uploaded_file.name}")
    
    if uploaded_file.type.startswith("text") or uploaded_file.name.endswith(".py"):
        file_contents = file_contents.decode("utf-8")
        st.code(file_contents[:1000], language="python")
    elif uploaded_file.type.startswith("image"):
        st.image(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
    

        with open("temp_uploaded.pdf", "wb") as f:
            f.write(file_contents)

        doc = fitz.open("temp_uploaded.pdf")
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()

        doc.close()

        st.text_area("📄 PDF Content Extracted:", pdf_text[:3000], height=300)
        file_contents = pdf_text  # Use in prompt


# --- Chat Interface ---
prompt = st.text_area("💬 Ask your coding question:", height=200)

if st.button("🧠 Send to Ollama"):
    full_prompt = prompt
    if file_contents:
        full_prompt += "\n\nHere is the file content:\n" + file_contents[:4000]

    with st.spinner("Thinking..."):
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        })

        if response.status_code == 200:
            answer = response.json()["response"]
            st.success("Ollama replied:")
            st.code(answer)
        else:
            st.error("Failed to get a response from Ollama.")









































# # streamlit_app.py
# import streamlit as st
# import requests

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL_NAME = "deepseek-coder:1.3b"

# st.title("💬 Local Code Assistant (Ollama + Streamlit)")
# user_input = st.text_area("Ask me about code:", height=150)

# if st.button("Send"):
#     with st.spinner("Thinking..."):
#         response = requests.post(OLLAMA_URL, json={
#             "model": MODEL,
#             "prompt": user_input,
#             "stream": False
#         })
#         st.code(response.json()["response"])

# uploaded_file = st.file_uploader("Upload a file", type=["py", "txt", "pdf", "png", "jpg"])
# if uploaded_file:
#     content = uploaded_file.read()
#     st.write("File uploaded:", uploaded_file.name)
#     # Do something: parse text, extract code, etc.
