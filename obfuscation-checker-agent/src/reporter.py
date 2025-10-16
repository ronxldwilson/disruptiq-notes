import json
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

class Reporter:
    def __init__(self, config):
        self.config = config
        self.findings = []

    def add_findings(self, findings: List):
        """Add findings to the report."""
        self.findings.extend(findings)

    def generate_report(self, scan_path: str) -> Dict[str, Any]:
        """Generate the full report dictionary."""
        now = datetime.utcnow().isoformat() + "Z"
        total_files = len(set(f.file_path for f in self.findings)) if self.findings else 0

        severity_counts = Counter(f.severity for f in self.findings)
        category_counts = Counter()
        confidence_scores = []

        # Store analyzer reference for pattern lookup
        analyzer = None
        try:
            from analyzer import Analyzer
            analyzer = Analyzer(self.config)
        except ImportError:
            pass

        # Analyze findings
        for finding in self.findings:
            # Count categories
            if analyzer and hasattr(analyzer, 'patterns'):
                pattern_info = analyzer.patterns.get(finding.obfuscation_type, {})
                category = pattern_info.get('category', 'unknown')
            else:
                category = 'unknown'
            category_counts[category] += 1

            # Collect confidence scores
            confidence_scores.append(finding.confidence)

        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        # Calculate risk score (weighted by severity and confidence)
        risk_score = 0
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        for finding in self.findings:
            weight = severity_weights.get(finding.severity, 1)
            risk_score += weight * finding.confidence

        report = {
            "scan_timestamp": now,
            "scan_path": scan_path,
            "total_files_scanned": total_files,
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "high_severity": severity_counts.get("high", 0),
                "medium_severity": severity_counts.get("medium", 0),
                "low_severity": severity_counts.get("low", 0),
                "total_findings": len(self.findings),
                "average_confidence": round(avg_confidence, 3),
                "risk_score": round(risk_score, 2),
                "categories": dict(category_counts)
            },
            "risk_assessment": self._assess_risk(severity_counts, category_counts, risk_score, total_files)
        }
        return report

    def _assess_risk(self, severity_counts: Counter, category_counts: Counter, risk_score: float, total_files: int) -> str:
        """Provide a risk assessment based on findings."""
        high_count = severity_counts.get("high", 0)
        medium_count = severity_counts.get("medium", 0)
        malware_signatures = category_counts.get("malware_signatures", 0)

        if high_count >= 3 or malware_signatures >= 2:
            return "CRITICAL: High likelihood of malicious obfuscation"
        elif high_count >= 1 or (medium_count >= 5 and risk_score > 10):
            return "HIGH: Significant obfuscation detected, manual review required"
        elif medium_count >= 3 or risk_score > 5:
            return "MEDIUM: Moderate obfuscation indicators present"
        elif severity_counts.get("low", 0) > 0:
            return "LOW: Minor obfuscation patterns detected"
        else:
            return "CLEAN: No significant obfuscation detected"

    def write_report(self, report: Dict[str, Any]):
        """Write the report to a JSON file."""
        output_file = self.config.get("output_file", "report.json")
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {output_file}")

    def print_summary(self, report: Dict[str, Any]):
        """Print a summary to console."""
        summary = report["summary"]
        print(f"\n{'='*60}")
        print(f"OBFUSCATION SCAN REPORT")
        print(f"{'='*60}")
        print(f"Scan Path: {report['scan_path']}")
        print(f"Timestamp: {report['scan_timestamp']}")
        print(f"Files Scanned: {report['total_files_scanned']}")
        print(f"Total Findings: {summary['total_findings']}")
        print()
        print("SEVERITY BREAKDOWN:")
        print(f"  High: {summary['high_severity']}")
        print(f"  Medium: {summary['medium_severity']}")
        print(f"  Low: {summary['low_severity']}")
        print()
        print("ANALYSIS METRICS:")
        print(".3f")
        print(".2f")
        print()
        print("CATEGORY BREAKDOWN:")
        for category, count in summary.get('categories', {}).items():
            print(f"  {category.replace('_', ' ').title()}: {count}")
        print()
        print(f"RISK ASSESSMENT: {report['risk_assessment']}")
        print(f"{'='*60}")
