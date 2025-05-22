import os
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
import faiss

# --- Config ---
PDF_FOLDER = "Data"
MODEL_NAME = "nomic-embed-text"
BASE_URL = "http://localhost:11434"
SAVE_DIR = "trained_model"

os.makedirs(SAVE_DIR, exist_ok=True)

# --- Load PDFs ---
pdfs = [
    os.path.join(root, file)
    for root, dirs, files in os.walk(PDF_FOLDER)
    for file in files
    if file.endswith(".pdf")
]

print(f"Found PDFs: {pdfs}")

# Load documents with PyMuPDFLoader
docs = []
for pdf in pdfs:
    loader = PyMuPDFLoader(pdf)
    pages = loader.load()
    docs.extend(pages)

print(f"Loaded {len(docs)} pages from PDFs")

# --- Chunk documents ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(docs)
print(f"Split into {len(chunks)} chunks")

# --- Embedding model ---
embedding_model = OllamaEmbeddings(model=MODEL_NAME, base_url=BASE_URL)

# Get vector dimension from sample embedding
sample_embedding = embedding_model.embed_query("test")
dim = len(sample_embedding)
print(f"Embedding dimension: {dim}")

# --- Create FAISS index ---
index = faiss.IndexFlatL2(dim)

# --- Create vector store ---
vector_store = FAISS(
    embedding_function=embedding_model,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

# Add docs to vector store
ids = vector_store.add_documents(chunks)
print(f"Added {len(ids)} documents to vector store")

# Save FAISS index + metadata
vector_store.save_local(SAVE_DIR)
print(f"Saved vector store to {SAVE_DIR}")
