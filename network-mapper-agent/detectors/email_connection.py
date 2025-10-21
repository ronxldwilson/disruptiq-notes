from detectors.base import Detector, Signal
import re

# Regex patterns for email/SMTP connections
EMAIL_PATTERNS = [
    re.compile(r'(?:smtplib\.SMTP|smtpssl\.SMTP_SSL)\s*\(\s*["\'][^"\']*["\']', re.IGNORECASE),
    re.compile(r'(?:nodemailer|mailgun|sendgrid|postmark)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:mail\.send|email\.send|smtp\.send)\s*\(\s*', re.IGNORECASE),
    re.compile(r'smtp://[^\s\'"]+', re.IGNORECASE),
    re.compile(r'(?:import smtplib|require.*nodemailer|from.*mailgun)', re.IGNORECASE),
]

class EmailConnectionDetector(Detector):
    id = "email_connection_v1"
    name = "Email Connection Detector"
    description = "Detects SMTP and email service connections"
    supported_languages = ["python", "javascript", "java", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in EMAIL_PATTERNS:
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
                    "id": f"emailconn-{file_path}-{line}-{hash(match_text)}",
                    "type": "email_connection",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "low"),
                    "confidence": 0.8,
                    "detail": f"Detected email/SMTP connection: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "email", "smtp"],
                    "remediation": "Review email sending code. Ensure SMTP credentials are secure and consider rate limits.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
