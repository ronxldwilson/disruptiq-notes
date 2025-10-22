class Finding:
    def __init__(self, file_path: str, line_number: int, obfuscation_type: str, description: str, severity: str, evidence: str, confidence: float = 1.0, full_line: str = "", category: str = "", id: int = None):
        self.file_path = file_path
        self.line_number = line_number
        self.obfuscation_type = obfuscation_type
        self.description = description
        self.severity = severity
        self.evidence = evidence
        self.confidence = confidence
        self.full_line = full_line
        self.category = category
        self.id = id

    def to_dict(self):
        return {
            "id": self.id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "obfuscation_type": self.obfuscation_type,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "full_line": self.full_line,
            "category": self.category
        }
