# src/parser_html.py
"""
Parse HTML 10-K files into structured JSON with sections.
We try to split by 'Item X' headings (Item 1, Item 1A, Item 7, Item 8, etc).
Output file: ../data/{COMPANY}_{YEAR}_parsed.json
"""

import re
import json
from bs4 import BeautifulSoup
import os

def load_html(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def split_into_sections(text):
    """
    Split text by lines that look like 'Item 1', 'ITEM 7.', 'Item 8.' etc.
    Returns list of dicts: [{'section': heading, 'text': content}, ...]
    """
    # Normalize section markers
    # We'll search case-insensitively for lines starting with "Item X"
    lines = text.splitlines()
    combined = []
    for ln in lines:
        ln2 = ln.strip()
        if ln2:
            combined.append(ln2)
    cleaned = "\n".join(combined)

    # find all positions of "Item <num>" headings
    pattern = re.compile(r'(^|\n)(item\s+\d+[a-z]?\b[^\n]*)', re.IGNORECASE)
    splits = []
    last_idx = 0
    # finditer returns match objects; we collect spans
    matches = list(pattern.finditer(cleaned))
    if not matches:
        # fallback: whole document as one section
        return [{"section": "full_text", "text": cleaned}]

    for i, m in enumerate(matches):
        start = m.start(2)
        heading = m.group(2).strip()
        # end is next match start or end of doc
        end = matches[i+1].start(2) if i+1 < len(matches) else len(cleaned)
        content = cleaned[start:end].strip()
        # separate heading line from rest
        # sometimes content includes heading; normalize:
        # split first newline
        parts = content.split("\n", 1)
        if len(parts) == 1:
            body = ""
        else:
            body = parts[1].strip()
        splits.append({"section": heading, "text": body})
    return splits

def parse_html_filing(file_path, company, year):
    html = load_html(file_path)
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts and styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # get textual content with some newlines preserved
    text = soup.get_text("\n", strip=True)
    sections = split_into_sections(text)

    result = {
        "company": company,
        "year": int(year),
        "source_file": os.path.basename(file_path),
        "sections": sections
    }
    return result

def save_parsed(result, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved parsed file to {out_path}")

if __name__ == "__main__":
    # quick test - update paths if needed
    infile = "../data/GOOGL_2023.htm"
    out = "../data/GOOGL_2023_parsed.json"
    res = parse_html_filing(infile, "GOOGL", 2023)
    save_parsed(res, out)
