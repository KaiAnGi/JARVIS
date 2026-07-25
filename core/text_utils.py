"""Shared text extraction utilities for plugins."""


def extract_after_keyword(text: str, keywords: tuple) -> str:
    """Extract text that follows one of the given keywords.

    Case-insensitive search. Returns the substring after the first matching
    keyword, stripped of whitespace. Returns "" if no match or nothing follows.
    """
    lower = text.lower()
    for kw in sorted(keywords, key=len, reverse=True):
        idx = lower.find(kw)
        if idx != -1:
            after = text[idx + len(kw) :].strip()
            if after:
                return after
    return ""
