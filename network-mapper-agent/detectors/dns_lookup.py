from detectors.base import Detector, Signal
import re

# Regex patterns for DNS lookups
DNS_PATTERNS = [
    re.compile(r'(?:socket\.gethostbyname|socket\.getaddrinfo)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:dns\.resolver|dns\.query)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:lookup|resolve)\s*\(\s*["\'][^"\']+\.[\w]+\.[\w]+["\']\s*\)', re.IGNORECASE),
    re.compile(r'(?:nslookup|dig|host)\s+', re.IGNORECASE),
    re.compile(r'(?:import dns|require.*dns)', re.IGNORECASE),
]

class DnsLookupDetector(Detector):
    id = "dns_lookup_v1"
    name = "DNS Lookup Detector"
    description = "Detects DNS resolution calls"
    supported_languages = ["python", "javascript", "java", "go", "rust"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in DNS_PATTERNS:
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
                    "id": f"dnslookup-{file_path}-{line}-{hash(match_text)}",
                    "type": "dns_lookup",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "low"),
                    "confidence": 0.7,
                    "detail": f"Detected DNS lookup: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "dns", "lookup"],
                    "remediation": "Review DNS resolution usage. Consider caching and error handling for DNS failures.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
