from detectors.base import Detector, Signal
import re

# Regex patterns for cloud SDK imports and usage
CLOUD_PATTERNS = [
    # AWS
    re.compile(r'(?:import boto3|from boto3|aws-sdk|boto\.|AWS\.)\s', re.IGNORECASE),
    # Google Cloud
    re.compile(r'(?:from google\.cloud|import google\.cloud|google-cloud-|gcp\.)\s', re.IGNORECASE),
    # Azure
    re.compile(r'(?:import azure|from azure|azure-|@azure/)\s', re.IGNORECASE),
    # Firebase
    re.compile(r'(?:import firebase|firebase\.|firebase-admin)\s', re.IGNORECASE),
    # Heroku
    re.compile(r'(?:heroku\.|heroku-cli|heroku-client)\s', re.IGNORECASE),
    # DigitalOcean
    re.compile(r'(?:digitalocean\.|python-digitalocean)\s', re.IGNORECASE),
    # Cloud client instantiations
    re.compile(r'(?:s3\.client|ec2\.client|gcs\.client|storage\.client)\s*\(\s*', re.IGNORECASE),
]

class CloudSdkDetector(Detector):
    id = "cloud_sdk_usage_v1"
    name = "Cloud SDK Usage Detector"
    description = "Detects usage of cloud service SDKs that make network calls"
    supported_languages = ["python", "javascript", "java", "go", "rust"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in CLOUD_PATTERNS:
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
                    "id": f"cloudsdk-{file_path}-{line}-{hash(match_text)}",
                    "type": "cloud_sdk_usage",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "medium"),
                    "confidence": 0.7,
                    "detail": f"Detected cloud SDK usage: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "cloud", "sdk"],
                    "remediation": "Review cloud service usage. Ensure proper authentication and monitor API costs/limits.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
