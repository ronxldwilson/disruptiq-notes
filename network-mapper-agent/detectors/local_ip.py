from detectors.base import Detector, Signal
import re

LOCAL_IP_RE = re.compile(r"(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})", re.IGNORECASE)

class LocalIpDetector(Detector):
    id = "local_ip_v1"
    name = "Local IP Detector"
    description = "Detects hardcoded local or private IPs"
    supported_languages = ["javascript", "python", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in LOCAL_IP_RE.finditer(file_content):
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
                "id": f"localip-{file_path}-{line}-{m.group(0)}",
                "type": "local_ip",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "low"),
                "confidence": 0.8,
                "detail": f"Detected hardcoded local or private IP: {m.group(0)}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["local", "internal", "ip", "hardcoded"],
                "remediation": "Avoid hardcoded private IPs; use service discovery or environment-based configuration.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "(10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}|192\\.168\\.\\d{1,3}\\.\\d{1,3}|172\\.(1[6-9]|2[0-9]|3[0-1])\\.\\d{1,3}\\.\\d{1,3})"
                }
            }

