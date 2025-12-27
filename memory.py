import os
import json
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY

# ---------------- CONFIG ----------------

EMBEDDING_DIM = 1536  # text-embedding-3-small
STORE_DIR = "memory_store"
INDEX_PATH = os.path.join(STORE_DIR, "faiss.index")
TEXT_PATH = os.path.join(STORE_DIR, "memory_texts.json")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------- INIT ----------------

os.makedirs(STORE_DIR, exist_ok=True)

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatL2(EMBEDDING_DIM)

if os.path.exists(TEXT_PATH):
    with open(TEXT_PATH, "r") as f:
        memory_texts: list[str] = json.load(f)
else:
    memory_texts: list[str] = []

# ---------------- EMBEDDING ----------------

def embed_text(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

# ---------------- PERSIST HELPERS ----------------

def persist():
    faiss.write_index(index, INDEX_PATH)
    with open(TEXT_PATH, "w") as f:
        json.dump(memory_texts, f, indent=2)

# ---------------- MEMORY API ----------------

def add_memory(text: str) -> None:
    if text in memory_texts:
        return  # hard dedupe

    vector = embed_text(text)
    index.add(vector.reshape(1, -1))
    memory_texts.append(text)
    persist()

def search_memory(query: str, k: int = 3) -> list[str]:
    if index.ntotal == 0:
        return []

    query_vector = embed_text(query)
    _, indices = index.search(query_vector.reshape(1, -1), k)

    results = []
    for idx in indices[0]:
        if idx != -1 and idx < len(memory_texts):
            results.append(memory_texts[idx])

    return results
