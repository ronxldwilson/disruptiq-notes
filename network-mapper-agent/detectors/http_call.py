from detectors.base import Detector, Signal
import re

# Separate regexes for different patterns to extract clean match text
HTTP_CALL_DOT_RE = re.compile(r"(fetch|axios|requests)\s*\.\s*(get|post|put|delete)", re.IGNORECASE)
HTTP_CALL_FETCH_RE = re.compile(r"\bfetch\s*\(", re.IGNORECASE)

class HttpCallDetector(Detector):
    id = "http_call_v1"
    name = "HTTP Call Detector"
    description = "Detects HTTP calls using common libraries"
    supported_languages = ["javascript", "python"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        # Match dot notation calls like axios.get, requests.post
        for m in HTTP_CALL_DOT_RE.finditer(file_content):
            start = m.start()
            line = file_content.count("\n", 0, start) + 1
            col = start - file_content.rfind("\n", 0, start)
            
            # Extract context around the match
            line_start = file_content.rfind("\n", 0, start)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1  # Move past the newline
            
            # Find end of the current line
            line_end = file_content.find("\n", start)
            if line_end == -1:
                line_end = len(file_content)
            
            # Get the full line containing the match
            snippet_line = file_content[line_start:line_end]
            
            # Get context (previous and next lines)
            prev_line_start = file_content.rfind("\n", 0, line_start-1)
            if prev_line_start == -1:
                prev_line_start = 0
            else:
                prev_line_start += 1  # Move past the newline
            prev_line = file_content[prev_line_start:line_start-1] if line_start > 1 else ""
            
            next_line_end = file_content.find("\n", line_end+1)
            if next_line_end == -1:
                next_line = ""
            else:
                next_line = file_content[line_end+1:next_line_end]
            
            match_text = f"{m.group(1)}.{m.group(2)}"
            
            yield {
                "id": f"httpcall-{file_path}-{line}-{match_text}",
                "type": "http_call",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "medium"),
                "confidence": 0.7,
                "detail": f"Detected HTTP call: {match_text}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["network", "http", "api"],
                "remediation": "Review the destination of the HTTP request. Consider using environment variables for endpoints rather than hardcoded URLs.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "(fetch|axios|requests)\\s*\\.\\s*(get|post|put|delete)"
                }
            }
        
        # Match standalone fetch calls separately to avoid the parentheses issue
        for m in HTTP_CALL_FETCH_RE.finditer(file_content):
            start = m.start()
            line = file_content.count("\n", 0, start) + 1
            col = start - file_content.rfind("\n", 0, start)
            
            # Extract context around the match
            line_start = file_content.rfind("\n", 0, start)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1  # Move past the newline
            
            # Find end of the current line
            line_end = file_content.find("\n", start)
            if line_end == -1:
                line_end = len(file_content)
            
            # Get the full line containing the match
            snippet_line = file_content[line_start:line_end]
            
            # Get context (previous and next lines)
            prev_line_start = file_content.rfind("\n", 0, line_start-1)
            if prev_line_start == -1:
                prev_line_start = 0
            else:
                prev_line_start += 1  # Move past the newline
            prev_line = file_content[prev_line_start:line_start-1] if line_start > 1 else ""
            
            next_line_end = file_content.find("\n", line_end+1)
            if next_line_end == -1:
                next_line = ""
            else:
                next_line = file_content[line_end+1:next_line_end]
            
            # Just use "fetch" as the match text
            match_text = "fetch"
            
            yield {
                "id": f"httpcall-{file_path}-{line}-{match_text}",
                "type": "http_call",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "medium"),
                "confidence": 0.7,
                "detail": f"Detected HTTP call: {match_text}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["network", "http", "api"],
                "remediation": "Review the destination of the HTTP request. Consider using environment variables for endpoints rather than hardcoded URLs.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "\\bfetch\\s*\\("
                }
            }

