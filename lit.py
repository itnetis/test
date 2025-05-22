import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- Config ---
MODEL_NAME_EMBED = "nomic-embed-text"
MODEL_NAME_LLM = "tinyllama"
BASE_URL = "http://localhost:11434"
VECTOR_STORE_DIR = "trained_model"

# --- Load vector store ---
embedding_model = OllamaEmbeddings(model=MODEL_NAME_EMBED, base_url=BASE_URL)
vector_store = FAISS.load_local(VECTOR_STORE_DIR, embeddings=embedding_model, allow_dangerous_deserialization=True)

retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 100})

# --- Load LLM ---
llm = ChatOllama(model=MODEL_NAME_LLM, base_url=BASE_URL)

# --- Setup prompt ---
prompt_template = """
You are a helpful assistant for answering questions based on the provided context only.
- Be direct and conversational.
- Avoid copying large chunks of raw content.
- Do not mention policies or academic rules unless directly asked.
- Do not invent or assume anything not in the context.

Context:
{context}

Question: {question}

Answer:
"""


prompt = ChatPromptTemplate.from_template(prompt_template)

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- Streamlit UI ---
st.set_page_config(page_title="Offline RAG Chatbot", layout="wide")
st.title("📚 Offline RAG Chatbot with Ollama & FAISS")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query = st.text_input("Ask a question:")

if query:
    # Get answer from RAG chain
    answer = rag_chain.invoke(query)
    st.session_state.chat_history.append((query, answer))

# Show chat history
for question, answer in reversed(st.session_state.chat_history):
    st.markdown(f"**You:** {question}")
    st.markdown(f"**Bot:** {answer}")
