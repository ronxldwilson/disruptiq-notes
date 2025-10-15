
from typing import List, Dict, Any, Iterable

class Signal(Dict):
    pass

class Detector:
    id: str  # e.g., "hardcoded_url_v1"
    name: str
    description: str
    supported_languages: List[str] = []
    default_severity: str = "medium"

    def __init__(self, config: Dict[str, Any]):
        """Load config (ruleset overrides, thresholds, enabled flag)"""
        self.config = config

    def match(self, file_path: str, file_content: str, ast: Any = None) -> Iterable[Signal]:
        """
        Analyze file (and AST if provided) and yield Signal dicts.
        Each Signal must follow the canonical schema (file, line, severity, detail, etc.)
        """
        raise NotImplementedError()
