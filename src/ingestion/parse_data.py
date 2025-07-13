# this class serves to parse the data produced by fetch_data.py and produces a clean and filtered list of data

import re

def clean_text(text):
    """
    cleans individual pieces of text by:
    - removing unwanted characters
    - collapsing whitespace
    - removing extra punctuation
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    text = re.sub(r"http\S+", "", text)                # remove URLs
    text = re.sub(r"[^A-Za-z0-9\s\.,%-]", "", text)    # remove non-text symbols
    text = re.sub(r"\s+", " ", text)                   # collapse multiple spaces
    text = re.sub(r"\.{3,}", "...", text)              # simplify ellipses
    text = text.strip()
    return text

def parse_input(content_list):
    """
    parses a list of strings and returns a cleaned, filtered list of meaningful inputs.
    """
    if not isinstance(content_list, list):
        raise ValueError("Input must be a list of strings.")

    cleaned = []
    seen = set()

    for item in content_list:
        if not isinstance(item, str):
            continue

        text = clean_text(item)

        if len(text) >= 10 and text not in seen:
            cleaned.append(text)
            seen.add(text)

    return cleaned
