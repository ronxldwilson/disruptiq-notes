from detectors.base import Detector, Signal
import re

# Regex to find src or href attributes with URLs
EXTERNAL_ASSET_RE = re.compile(r'<[^>]*\b(src|href)\s*=\s*["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)

class ExternalAssetDetector(Detector):
    id = "external_asset_v1"
    name = "External Asset Detector"
    description = "Detects external assets loaded in HTML files (e.g., images, scripts, stylesheets)"
    supported_languages = ["html"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for m in EXTERNAL_ASSET_RE.finditer(file_content):
            attr_name = m.group(1)  # 'src' or 'href'
            url = m.group(2)

            # Check if it's an absolute URL (starts with http:// or https://)
            if url.startswith(('http://', 'https://')):
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
                    "id": f"externalasset-{file_path}-{line}-{url}",
                    "type": "asset_load",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "medium"),
                    "confidence": 0.9,
                    "detail": f"External asset loaded: {url}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "asset", "http"],
                    "remediation": "Review external asset loading. Consider hosting assets locally or ensuring the external domain is trusted.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": r'<[^>]*\b(src|href)\s*=\s*["\']([^"\']+)["\'][^>]*>',
                        "url": url,
                        "attribute": attr_name
                    }
                }
