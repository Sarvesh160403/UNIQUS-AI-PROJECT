import os
import faiss
import numpy as np
import json
from src.embedder import embed_texts

# Base paths (always relative to project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
META_PATH = os.path.join(DATA_DIR, "chunks_meta.json")
EMB_PATH = os.path.join(DATA_DIR, "embeddings.npy")

def build_index_from_npy(embeddings_path=EMB_PATH, meta_path=META_PATH, index_out=INDEX_PATH):
    embeddings = np.load(embeddings_path)
    # normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)  # inner product on normalized vectors = cosine
    index.add(embeddings)
    faiss.write_index(index, index_out)
    print(f"FAISS index built and saved to {index_out}")
    return index

def load_index_and_meta(index_path=INDEX_PATH, meta_path=META_PATH):
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Index or meta not found. Run build_index first.")
    index = faiss.read_index(index_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta

def search_query(query, top_k=5):
    index, meta = load_index_and_meta()
    q_emb = embed_texts([query])
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        item = meta[idx].copy()
        item["score"] = float(score)
        # include short excerpt
        item["excerpt"] = item["text"][:500].replace("\n", " ")
        results.append(item)
    return results
