# src/embedder.py
"""
Embed text chunks using sentence-transformers (all-MiniLM-L6-v2).
Saves embeddings.npy and chunks metadata in pkl/json.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import json, os

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL = SentenceTransformer(MODEL_NAME)

def embed_texts(texts, batch_size=64):
    embs = MODEL.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True)
    return embs

def embed_chunks_and_save(chunks_json_path, embeddings_out_path="../data/embeddings.npy", meta_out_path="../data/chunks_meta.json"):
    with open(chunks_json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    # save embeddings and metadata
    np.save(embeddings_out_path, embeddings)
    with open(meta_out_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved embeddings ({embeddings.shape}) to {embeddings_out_path} and meta to {meta_out_path}")
    return embeddings, chunks

if __name__ == "__main__":
    emb, chunks = embed_chunks_and_save("../data/GOOGL_2023_chunks.json")
