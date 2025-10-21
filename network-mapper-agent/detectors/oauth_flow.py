from detectors.base import Detector, Signal
import re

# Regex patterns for OAuth flows
OAUTH_PATTERNS = [
    re.compile(r'(?:oauth2\.|OAuth2|oauthlib)\s', re.IGNORECASE),
    re.compile(r'(?:passport\.|passport-oauth)', re.IGNORECASE),
    re.compile(r'(?:token.*refresh|access_token.*exchange)', re.IGNORECASE),
    re.compile(r'(?:authorization_code|implicit_flow|client_credentials)', re.IGNORECASE),
    re.compile(r'(?:import.*oauth|require.*passport)', re.IGNORECASE),
    re.compile(r'(?:google-auth|auth0|okta)', re.IGNORECASE),
]

class OauthFlowDetector(Detector):
    id = "oauth_flow_v1"
    name = "OAuth Flow Detector"
    description = "Detects OAuth authentication flows and token handling"
    supported_languages = ["python", "javascript", "java", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in OAUTH_PATTERNS:
            for m in pattern.finditer(file_content):
                start = m.start()
                line = file_content.count("\n", 0, start) + 1
                col = start - file_content.rfind("\n", 0, start)

                # Extract context
                line_start = file_content.rfind("\n", 0, start)
                if line_start == -1:
                    line_start = 0
                else:
                    line_start += 1

                line_end = file_content.find("\n", start)
                if line_end == -1:
                    line_end = len(file_content)

                snippet_line = file_content[line_start:line_end]

                prev_line_start = file_content.rfind("\n", 0, line_start-1)
                if prev_line_start == -1:
                    prev_line_start = 0
                else:
                    prev_line_start += 1
                prev_line = file_content[prev_line_start:line_start-1] if line_start > 1 else ""

                next_line_end = file_content.find("\n", line_end+1)
                if next_line_end == -1:
                    next_line = ""
                else:
                    next_line = file_content[line_end+1:next_line_end]

                match_text = m.group(0).strip()

                yield {
                    "id": f"oauth-{file_path}-{line}-{hash(match_text)}",
                    "type": "oauth_flow",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "low"),
                    "confidence": 0.7,
                    "detail": f"Detected OAuth flow: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "oauth", "authentication"],
                    "remediation": "Review OAuth implementation. Ensure secure token storage and proper scope handling.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
