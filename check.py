import os
import faiss
from openai import OpenAI
from config import OPENAI_API_KEY
import numpy as np


client = OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_DIM = 1536  # text-embedding-3-small
STORE_DIR = "memory_store"
INDEX_PATH = os.path.join(STORE_DIR, "faiss.index")
TEXT_PATH = os.path.join(STORE_DIR, "memory_texts.json")


def embed_text(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

index = faiss.read_index(INDEX_PATH)
def search_memory(query: str, k: int = 3) -> list[str]:
    if index.ntotal == 0:
        return []

    query_vector = embed_text(query)
    _, indices = index.search(query_vector.reshape(1, -1), k)

    print(indices)

search_memory("sample query")


#APIs
# key -> X25Twm6aoFGJGBFpsUD5Av54vSl56zf7
# secret key -> aSIwziKMu6vsmgw1