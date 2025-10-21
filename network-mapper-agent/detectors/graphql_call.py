from detectors.base import Detector, Signal
import re

# Regex patterns for GraphQL usage
GRAPHQL_PATTERNS = [
    re.compile(r'(?:apollo-client|graphql-request|gql|react-apollo)\s', re.IGNORECASE),
    re.compile(r'(?:graphql\.|GraphQLClient)\s*\(\s*', re.IGNORECASE),
    re.compile(r'query\s*\{[^}]*\}|mutation\s*\{[^}]*\}', re.IGNORECASE),  # GraphQL query syntax
    re.compile(r'(?:import.*graphql|require.*graphql)', re.IGNORECASE),
    re.compile(r'(?:useQuery|useMutation|useLazyQuery)\s*\(\s*', re.IGNORECASE),
]

class GraphqlCallDetector(Detector):
    id = "graphql_call_v1"
    name = "GraphQL Call Detector"
    description = "Detects GraphQL client usage and queries"
    supported_languages = ["javascript", "typescript", "python"]

    def __init__(self, config):
        super().__init__(config)

    def match(self, file_path, file_content, ast=None):
        for pattern in GRAPHQL_PATTERNS:
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
                    "id": f"graphql-{file_path}-{line}-{hash(match_text)}",
                    "type": "graphql_call",
                    "detector_id": self.id,
                    "file": file_path,
                    "line": line,
                    "column": col,
                    "severity": self.config.get("severity", "medium"),
                    "confidence": 0.8,
                    "detail": f"Detected GraphQL usage: {match_text}",
                    "context": {
                        "snippet": snippet_line.strip(),
                        "pre": prev_line.strip(),
                        "post": next_line.strip()
                    },
                    "tags": ["network", "graphql", "api"],
                    "remediation": "Review GraphQL queries and mutations. Ensure proper error handling and consider query complexity.",
                    "evidence": {
                        "match": m.group(0),
                        "regex": str(pattern.pattern)
                    }
                }
