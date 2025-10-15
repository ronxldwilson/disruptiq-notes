from detectors.base import Detector, Signal
import re

RAW_SOCKET_RE = re.compile(r"socket\.socket\(|net\.Socket\(", re.IGNORECASE)

class RawSocketDetector(Detector):
    id = "raw_socket_v1"
    name = "Raw Socket Detector"
    description = "Detects raw socket usage"
    supported_languages = ["python", "javascript"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in RAW_SOCKET_RE.finditer(file_content):
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
            
            yield {
                "id": f"rawsocket-{file_path}-{line}-{m.group(0)}",
                "type": "raw_socket_usage",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "medium"),
                "confidence": 0.8,
                "detail": f"Detected raw socket usage: {m.group(0)}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["network", "low-level", "socket"],
                "remediation": "Consider using higher-level networking libraries rather than raw sockets when possible. Raw sockets are harder to secure.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "socket\\.socket\\(|net\\.Socket\\("
                }
            }

