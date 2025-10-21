from detectors.base import Detector, Signal
import re

# Regex patterns for database connection strings and client instantiations
DB_PATTERNS = [
    # MongoDB
    re.compile(r'(?:pymongo\.|mongo_client\.|MongoClient)\s*\(\s*["\'][^"\']*["\']', re.IGNORECASE),
    # Redis
    re.compile(r'(?:redis\.Redis|redis\.StrictRedis)\s*\(\s*(?:host|url)', re.IGNORECASE),
    # PostgreSQL
    re.compile(r'(?:psycopg2\.connect|sqlalchemy\.create_engine)\s*\(\s*(?:host|url)', re.IGNORECASE),
    # MySQL
    re.compile(r'(?:pymysql\.connect|mysql\.connector\.connect)\s*\(\s*host', re.IGNORECASE),
    # Cassandra
    re.compile(r'cassandra\.Cluster\s*\(\s*["\'][^"\']*["\']', re.IGNORECASE),
    # Elasticsearch
    re.compile(r'(?:elasticsearch\.Elasticsearch|es\.Elasticsearch)\s*\(\s*hosts?', re.IGNORECASE),
    # Generic connection strings
    re.compile(r'(?:connection_string|conn_str|db_url|database_url)\s*[:=]\s*["\'][^"\']*(?:mongodb|redis|postgres|mysql|cassandra|elasticsearch)[^"\']*["\']', re.IGNORECASE),
]

class DatabaseConnectionDetector(Detector):
    id = "database_connection_v1"
    name = "Database Connection Detector"
    description = "Detects network connections to remote databases"
    supported_languages = ["python", "javascript", "java", "go", "rust"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in DB_PATTERNS:
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

                match_text = m.group(0)[:50]  # Truncate long matches

                yield {
                    "id": f"dbconn-{file_path}-{line}-{hash(match_text)}",
                    "type": "database_connection",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "medium"),
                    "confidence": 0.8,
                    "detail": f"Detected potential database connection: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "database", "connection"],
                    "remediation": "Review database connection strings. Ensure credentials are not hardcoded and connections use secure protocols.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
