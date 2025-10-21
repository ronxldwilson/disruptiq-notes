from detectors.base import Detector, Signal
import re

# Regex patterns for web scraping libraries
SCRAPING_PATTERNS = [
    re.compile(r'(?:BeautifulSoup|bs4\.BeautifulSoup)\s*\(\s*', re.IGNORECASE),
    re.compile(r'(?:selenium\.webdriver|puppeteer|playwright)\s', re.IGNORECASE),
    re.compile(r'(?:requests\.get|urllib\.request)\s*\(\s*["\'][^"\']+\.html?["\']\s*\)', re.IGNORECASE),
    re.compile(r'(?:scrapy\.Spider|scrapy\.CrawlSpider)', re.IGNORECASE),
    re.compile(r'(?:import.*BeautifulSoup|import.*selenium|require.*puppeteer)', re.IGNORECASE),
    re.compile(r'(?:cheerio\.load|jsdom)', re.IGNORECASE),
]

class WebScrapingDetector(Detector):
    id = "web_scraping_v1"
    name = "Web Scraping Detector"
    description = "Detects web scraping libraries and automated browsing"
    supported_languages = ["python", "javascript"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in SCRAPING_PATTERNS:
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
                    "id": f"scraping-{file_path}-{line}-{hash(match_text)}",
                    "type": "web_scraping",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "high"),
                    "confidence": 0.8,
                    "detail": f"Detected web scraping usage: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "scraping", "automation"],
                    "remediation": "Review web scraping implementation. Ensure compliance with terms of service and implement rate limiting.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
