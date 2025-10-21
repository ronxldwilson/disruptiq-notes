from detectors.base import Detector, Signal
import re

# Regex patterns for FTP/SFTP connections
FTP_PATTERNS = [
    re.compile(r'(?:ftplib\.FTP|ftplib\.FTP_TLS)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:paramiko\.SSHClient|paramiko\.Transport)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:ssh2\.Client|ssh2\.Session)\s*\(\s*', re.IGNORECASE),
    re.compile(r'ftp://[^\s\'"]+', re.IGNORECASE),
    re.compile(r'sftp://[^\s\'"]+', re.IGNORECASE),
    re.compile(r'(?:import ftplib|import paramiko|require.*ssh2)', re.IGNORECASE),
]

class FtpConnectionDetector(Detector):
    id = "ftp_connection_v1"
    name = "FTP Connection Detector"
    description = "Detects FTP and SFTP connections"
    supported_languages = ["python", "javascript", "java", "go"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in FTP_PATTERNS:
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
                    "id": f"ftpconn-{file_path}-{line}-{hash(match_text)}",
                    "type": "ftp_connection",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "medium"),
                    "confidence": 0.8,
                    "detail": f"Detected FTP/SFTP connection: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "ftp", "sftp", "file_transfer"],
                    "remediation": "Review FTP/SFTP usage. Prefer SFTP over FTP and ensure secure authentication.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
