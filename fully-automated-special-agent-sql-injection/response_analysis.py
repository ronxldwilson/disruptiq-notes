
import re

ERROR_PATTERNS = [
    re.compile(r"you have an error in your sql syntax", re.I),
    re.compile(r"syntax error at or near", re.I),
    re.compile(r"unrecognized token", re.I),
]

def analyze_response(text):
    for p in ERROR_PATTERNS:
        if p.search(text or ""):
            return True, p.pattern
    return False, None
