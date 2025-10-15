from detectors.base import Detector, Signal
import re

CORS_RE = re.compile(r"cors\s*\(\s*{\s*['\"]?origin['\"]?\s*:\s*['\"]\*['\"]\s*}\s*\)", re.IGNORECASE)

class CorsPolicyDetector(Detector):
    id = "cors_policy_v1"
    name = "CORS Policy Detector"
    description = "Detects permissive CORS policies"
    supported_languages = ["javascript"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in CORS_RE.finditer(file_content):
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
                "id": f"cors-{file_path}-{line}-{m.group(0)}",
                "type": "cors_policy",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "high"),
                "confidence": 0.9,
                "detail": f"Detected permissive CORS policy: {m.group(0)}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["security", "cors", "permissive"],
                "remediation": "Restrict origin to specific domains. Do not use wildcard origin in production environments.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "cors\\s*\\(\\s*{\\s*origin\\s*:\\s*['\"]\\*['\"]\\s*}\\s*\\)"
                }
            }

