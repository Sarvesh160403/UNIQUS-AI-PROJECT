# src/build_index.py
"""
Orchestration script:
- Parse all GOOGL .htm filings in ../data
- Create parsed JSONs
- Chunk into smaller pieces
- Embed chunks
- Build FAISS index
"""

import glob
import os
import json

from src.parser_html import parse_html_filing, save_parsed
from src.chunker import parsed_json_to_chunks
from src.embedder import embed_chunks_and_save
from src.vector_store import build_index_from_npy

# 🔹 Base project folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Make sure data/ exists
os.makedirs(DATA_DIR, exist_ok=True)

def process_one(file_path):
    base = os.path.basename(file_path)  # e.g. GOOGL_2023.htm
    parts = base.split("_")
    company = parts[0]
    year = parts[1].split(".")[0]

    parsed_out = os.path.join(DATA_DIR, f"{company}_{year}_parsed.json")
    parsed = parse_html_filing(file_path, company, year)
    save_parsed(parsed, parsed_out)

    chunks_out = os.path.join(DATA_DIR, f"{company}_{year}_chunks.json")
    parsed_json_to_chunks(parsed_out, chunks_out)
    return chunks_out

def main():
    # Find all GOOGL filings in data/
    htm_files = glob.glob(os.path.join(DATA_DIR, "GOOGL_*.htm"))
    if not htm_files:
        print("❌ No GOOGL .htm files found in data/. Please add them first.")
        return

    all_chunk_paths = []
    for f in htm_files:
        print("📄 Processing", f)
        chunks_json = process_one(f)
        all_chunk_paths.append(chunks_json)

    # Combine all chunks
    combined_chunks = []
    for p in all_chunk_paths:
        with open(p, "r", encoding="utf-8") as fh:
            arr = json.load(fh)
            combined_chunks.extend(arr)

    combined_path = os.path.join(DATA_DIR, "GOOGL_all_chunks.json")
    with open(combined_path, "w", encoding="utf-8") as out:
        json.dump(combined_chunks, out, ensure_ascii=False, indent=2)
    print(f"✅ Combined chunks saved → {combined_path}")

    # Embed and save
    emb_path = os.path.join(DATA_DIR, "embeddings.npy")
    meta_path = os.path.join(DATA_DIR, "chunks_meta.json")
    embed_chunks_and_save(combined_path, embeddings_out_path=emb_path, meta_out_path=meta_path)

    # Build FAISS index
    index_out = os.path.join(DATA_DIR, "faiss_index.bin")
    build_index_from_npy(embeddings_path=emb_path, meta_path=meta_path, index_out=index_out)
    print(f"✅ FAISS index built → {index_out}")

if __name__ == "__main__":
    main()
