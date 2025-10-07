# src/chunker.py
"""
Convert parsed JSON sections into smaller text chunks for embeddings.
"""

import re, json, uuid

def sent_tokenize(text):
    # Simple regex-based sentence splitter (no NLTK needed)
    return re.split(r'(?<=[\.\!\?])\s+', text)

def chunk_text_by_sentences(text, chunk_size_chars=3000, overlap_chars=300):
    sentences = sent_tokenize(text)
    chunks = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) <= chunk_size_chars:
            cur += " " + s
        else:
            chunks.append(cur.strip())
            cur = cur[-overlap_chars:] + " " + s
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def parsed_json_to_chunks(parsed_json_path, out_chunks_path):
    with open(parsed_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    company = data.get("company")
    year = data.get("year")
    sections = data.get("sections", [])

    all_chunks = []
    for sec in sections:
        section_name = sec.get("section", "unknown")
        text = sec.get("text", "")
        if not text or len(text) < 50:
            continue
        for ch in chunk_text_by_sentences(text):
            all_chunks.append({
                "id": str(uuid.uuid4()),
                "company": company,
                "year": year,
                "section": section_name,
                "text": ch,
                "char_len": len(ch)
            })

    with open(out_chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ Wrote {len(all_chunks)} chunks → {out_chunks_path}")
    return all_chunks

if __name__ == "__main__":
    # Example test
    parsed = "../data/GOOGL_2022_parsed.json"
    out = "../data/GOOGL_2022_chunks.json"
    parsed_json_to_chunks(parsed, out)
