from detectors.base import Detector, Signal
import re

THIRD_PARTY_SDK_RE = re.compile(r"segment\.track|mixpanel\.track|google\.analytics", re.IGNORECASE)

class ThirdPartySdkDetector(Detector):
    id = "third_party_sdk_v1"
    name = "Third Party SDK Detector"
    description = "Detects usage of analytics/telemetry libraries"
    supported_languages = ["javascript", "python"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in THIRD_PARTY_SDK_RE.finditer(file_content):
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
                "id": f"thirdpartysdk-{file_path}-{line}-{m.group(0)}",
                "type": "third_party_sdk_usage",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "info"),
                "confidence": 0.7,
                "detail": f"Detected third-party SDK usage: {m.group(0)}",
                "context": {
                    "snippet": snippet_line.strip(),
                    "pre": prev_line.strip(),
                    "post": next_line.strip()
                },
                "tags": ["tracking", "analytics", "telemetry", "privacy"],
                "remediation": "Review third-party SDK usage for privacy implications. Ensure compliance with data protection regulations.",
                "evidence": {
                    "match": m.group(0),
                    "regex": "segment\\.track|mixpanel\\.track|google\\.analytics"
                }
            }

