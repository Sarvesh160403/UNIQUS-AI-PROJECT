# src/utils.py
"""
Utility parsers for extracting monetary values and percentages from text.
These are best-effort regex parsers (not perfect) but handle common patterns:
 - $12,345,678
 - 12,345 (in millions)
 - $12.3 billion
 - 45.6%
"""

import re

def parse_money(text):
    """
    Try to find a monetary amount and normalize to float (absolute USD).
    Returns dict {'value': float_in_usd, 'raw': matched_text, 'scale': 'million|billion|', 'unit': 'USD'}
    If not found, returns None.
    """
    # common pattern: $12,345 or 12,345 million or $12.3 billion
    # First try explicit $numbers
    m = re.search(r'\$[\s]*([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.[0-9]+)?)(?:\s*(million|billion|thousand|m|bn))?', text, re.I)
    if m:
        num_str = m.group(1)
        scale = m.group(2) or ""
        num = float(num_str.replace(",", ""))
        scale = scale.lower()
        if "million" in scale or scale == "m":
            num = num * 1e6
        elif "billion" in scale or scale == "bn":
            num = num * 1e9
        elif "thousand" in scale:
            num = num * 1e3
        return {"value": num, "raw": m.group(0), "scale": scale, "unit": "USD"}

    # try patterns like "12,345 million"
    m2 = re.search(r'([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.[0-9]+)?)\s*(million|billion|thousand|m|bn)\s*(?:of|in)?\s*(dollars)?', text, re.I)
    if m2:
        num = float(m2.group(1).replace(",", ""))
        scale = m2.group(2).lower()
        if "million" in scale or scale == "m":
            num = num * 1e6
        elif "billion" in scale or scale == "bn":
            num = num * 1e9
        elif "thousand" in scale:
            num = num * 1e3
        return {"value": num, "raw": m2.group(0), "scale": scale, "unit": "USD"}

    # Try bare numbers that follow words like 'revenue' and maybe mention 'in millions'
    m3 = re.search(r'(revenue|total revenue|net revenue|net sales)[^\d\n\r]{0,30}([0-9][0-9,\.]+)', text, re.I)
    if m3:
        num = float(m3.group(2).replace(",", ""))
        return {"value": num, "raw": m3.group(2), "scale": "", "unit": "USD"}

    return None

def parse_percent(text):
    m = re.search(r'([0-9]{1,3}(?:\.[0-9]+)?)\s*%', text)
    if m:
        return float(m.group(1))
    # patterns like "grew by 12 percent"
    m2 = re.search(r'([0-9]{1,3}(?:\.[0-9]+)?)\s*(percent|percentage)', text, re.I)
    if m2:
        return float(m2.group(1))
    return None
