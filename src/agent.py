# src/agent.py
"""
Agent logic for Google-only pipeline.
- decompose(query): create subqueries (e.g., revenue 2023, revenue 2022)
- run_subqueries: call vector_store.search for each subquery
- extract numbers using utils.parse_money and parse_percent
- synthesize JSON with answer, reasoning, sub_queries, and sources
"""

import re
from src.vector_store import search_query
from src.utils import parse_money, parse_percent


def need_decomposition(query: str) -> bool:
    q = query.lower()
    if re.search(r'from\s+20\d{2}\s+to\s+20\d{2}', q): return True
    if "compare" in q or "growth" in q or "how did" in q or "change" in q: return True
    # percentage-of-revenue patterns
    if re.search(r'percentage of .* revenue|% of .* revenue|what percentage', q): return True
    return False

def decompose(query: str):
    q = query.lower()
    years = re.findall(r'(20\d{2})', q)
    # Common patterns
    if "percentage" in q and "revenue" in q and "advert" in q:
        # advertising share of total revenue for a year
        year = years[0] if years else None
        subs = []
        if year:
            subs.append(f"Google advertising revenue {year}")
            subs.append(f"Google total revenue {year}")
        else:
            subs.append("Google advertising revenue")
            subs.append("Google total revenue")
        return subs

    # growth e.g., "How did Google's cloud revenue grow from 2022 to 2023?"
    m = re.search(r'from\s+(20\d{2})\s+to\s+(20\d{2})', q)
    if m:
        y1, y2 = m.group(1), m.group(2)
        # try to find metric in query
        if "data center" in q or "cloud" in q or "cloud revenue" in q:
            metric = "cloud revenue"
        elif "revenue" in q:
            metric = "total revenue"
        else:
            metric = "revenue"
        return [f"Google {metric} {y1}", f"Google {metric} {y2}"]

    # default: ask simple retrieval for the query
    return [query]

def run_subquery_and_extract(subq):
    retrieved = search_query(subq, top_k=6)
    # try to extract a number from top results
    for r in retrieved:
        text = r.get("text", "")
        money = parse_money(text)
        if money:
            return {"sub_query": subq, "value": money["value"], "raw": money["raw"], "source": r}
        pct = parse_percent(text)
        if pct is not None:
            return {"sub_query": subq, "value_percent": pct, "raw": f"{pct}%", "source": r}
    # fallback: return top retrieved snippet without number
    if retrieved:
        r = retrieved[0]
        return {"sub_query": subq, "value": None, "raw": None, "source": r}
    return {"sub_query": subq, "value": None, "raw": None, "source": None}

def pct_change(old, new):
    if old is None or new is None: return None
    if old == 0: return None
    return (new - old) / old * 100.0

def synthesize(query):
    if need_decomposition(query):
        subqs = decompose(query)
    else:
        subqs = [query]

    results = []
    for sq in subqs:
        res = run_subquery_and_extract(sq)
        results.append(res)

    # Build answer depending on type
    answer = ""
    reasoning = ""
    sources = []

    # Example: percentage-of-revenue advertising: subqs = [adv_rev, total_rev]
    if len(results) == 2 and results[0].get("value") and results[1].get("value"):
        v_adv = results[0]["value"]
        v_tot = results[1]["value"]
        pct = (v_adv / v_tot) * 100 if v_tot else None
        # format numbers nicely (rounded)
        answer = f"{results[0]['source']['company']} advertising revenue was {v_adv:,.0f} USD and total revenue was {v_tot:,.0f} USD, so advertising was {pct:.2f}% of revenue."
        reasoning = f"Extracted advertising and total revenue from 10-K chunks and computed advertising/total * 100."
        for r in results:
            src = r["source"]
            if src:
                sources.append({
                    "company": src.get("company"),
                    "year": str(src.get("year")),
                    "excerpt": src.get("excerpt"),
                    "section": src.get("section")
                })
    # Example: YoY growth with two values
    elif len(results) == 2 and results[0].get("value") is not None and results[1].get("value") is not None:
        old = results[0]["value"]; new = results[1]["value"]
        change = pct_change(old, new)
        answer = f"{results[0]['source']['company']} {results[0]['sub_query']} -> {old:,.0f} USD; {results[1]['sub_query']} -> {new:,.0f} USD. Growth = {change:.2f}%."
        reasoning = "Retrieved values for the two years and computed percentage growth."
        for r in results:
            src = r["source"]
            if src:
                sources.append({
                    "company": src.get("company"),
                    "year": str(src.get("year")),
                    "excerpt": src.get("excerpt"),
                    "section": src.get("section")
                })
    else:
        # Generic: return top excerpts
        parts = []
        for r in results:
            src = r.get("source")
            if src:
                parts.append(f"Sub-query: {r['sub_query']}\nExcerpt: {src.get('excerpt')}\n")
                sources.append({
                    "company": src.get("company"),
                    "year": str(src.get("year")),
                    "excerpt": src.get("excerpt"),
                    "section": src.get("section")
                })
        answer = "\n\n".join(parts) if parts else "No information found in the parsed 10-K chunks."
        reasoning = "Returned top retrieved excerpts because numeric extraction failed or query was open-ended."

    return {
        "query": query,
        "answer": answer,
        "reasoning": reasoning,
        "sub_queries": [r["sub_query"] for r in results],
        "sources": sources
    }

if __name__ == "__main__":
    q = "What percentage of Google's 2023 revenue came from advertising?"
    out = synthesize(q)
    import json
    print(json.dumps(out, indent=2))
