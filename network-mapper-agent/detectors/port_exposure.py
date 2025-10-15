from detectors.base import Detector, Signal
import re

PORT_RE = re.compile(r"(listen|bind|serve)\s*\(\s*(\d{2,5})\b", re.IGNORECASE)

class PortExposureDetector(Detector):
    id = "port_exposure_v1"
    name = "Port Exposure Detector"
    description = "Detects server port exposures"
    supported_languages = ["javascript", "python", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in PORT_RE.finditer(file_content):
            start = m.start(2)
            line = file_content.count("\n", 0, start) + 1
            col = start - file_content.rfind("\n", 0, start)
            port = m.group(2)
            
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
                "id": f"portexp-{file_path}-{line}-{port}",
                "type": "port_exposure",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "high"),
                "confidence": 0.8,
                "detail": f"Detected port exposure: {port}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["exposed", "http", "server", "port"],
                "remediation": "Enable TLS or proxy behind reverse-proxy with TLS. Avoid binding insecure port in production.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "(listen|bind|serve)\\s*\\(\\s*(\\d{2,5})\\s*\\)",
                    "match_groups": {"1": m.group(1), "2": m.group(2)}
                }
            }

