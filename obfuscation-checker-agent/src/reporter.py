import aiofiles
import json
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

class Reporter:
    def __init__(self, config):
        self.config = config
        self.findings = []
        # Pre-computed aggregates for efficiency
        self.severity_counts = Counter()
        self.category_counts = Counter()
        self.confidence_scores = []
        self.total_risk_score = 0.0
        self.total_findings_count = 0
        self.next_id = 1
        self.shutdown_check = lambda: False

    def add_findings(self, findings: List):
        """Add findings to the report."""
        # Assign auto-incrementing IDs
        for finding in findings:
            finding.id = self.next_id
            self.next_id += 1
        self.findings.extend(findings)
        # Update aggregates incrementally
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        for finding in findings:
            self.severity_counts[finding.severity] += 1
            self.category_counts[finding.category] += 1
            self.confidence_scores.append(finding.confidence)
            weight = severity_weights.get(finding.severity, 1)
            self.total_risk_score += weight * finding.confidence
            self.total_findings_count += 1

    def generate_report(self, scan_path: str, elapsed_time: float = None, total_files_scanned: int = None) -> Dict[str, Any]:
        """Generate the full report dictionary."""
        now = datetime.utcnow().isoformat() + "Z"
        total_files = total_files_scanned if total_files_scanned is not None else (len(set(f.file_path for f in self.findings)) if self.findings else 0)

        # Use pre-computed aggregates
        severity_counts = self.severity_counts
        category_counts = self.category_counts
        confidence_scores = self.confidence_scores

        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        # Use pre-computed risk score
        risk_score = self.total_risk_score

        summary = {
            "high_severity": severity_counts.get("high", 0),
            "medium_severity": severity_counts.get("medium", 0),
            "low_severity": severity_counts.get("low", 0),
            "total_findings": self.total_findings_count,
            "average_confidence": round(avg_confidence, 3),
            "risk_score": round(risk_score, 2),
            "categories": dict(category_counts)
        }
        report = {
            "scan_timestamp": now,
            "scan_path": scan_path,
            "total_files_scanned": total_files,
            "summary": summary,
            "scan_duration_seconds": round(elapsed_time, 2) if elapsed_time is not None else None,
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

    async def write_report(self, report: Dict[str, Any], is_final: bool = False, quiet: bool = False):
        """Write the report to a JSON file asynchronously, streaming to minimize memory usage."""
        output_file = self.config.get("output_file", "output.json")
        async with aiofiles.open(output_file, 'w') as f:
            # Write the report structure, streaming findings to avoid loading all into memory
            await f.write('{\n')
            await f.write(f'  "scan_timestamp": {json.dumps(report["scan_timestamp"])},\n')
            await f.write(f'  "scan_path": {json.dumps(report["scan_path"])},\n')
            await f.write(f'  "total_files_scanned": {report["total_files_scanned"]},\n')
            await f.write('  "findings": [\n')
            # Stream findings directly from self.findings
            total_findings = len(self.findings)
            for i, finding in enumerate(self.findings):
                if self.shutdown_check():
                    print("Shutdown requested during report writing, aborting.")
                    break
                comma = ',' if i < len(self.findings) - 1 else ''
                finding_dict = finding.to_dict()
                # Write each finding as properly indented JSON
                finding_json = json.dumps(finding_dict, indent=4)
                # Indent it properly in the array
                indented = '\n'.join('    ' + line for line in finding_json.split('\n'))
                await f.write(f'{indented}{comma}\n')
                # Show progress for large final reports
                if is_final and total_findings > 100 and (i + 1) % 100 == 0:
                    progress = (i + 1) / total_findings * 100
                    print(f"Report writing progress: {i + 1}/{total_findings} findings ({progress:.1f}%)")
            await f.write('  ],\n')
            await f.write('  "summary": {\n')
            summary = report["summary"]
            await f.write(f'    "high_severity": {summary["high_severity"]},\n')
            await f.write(f'    "medium_severity": {summary["medium_severity"]},\n')
            await f.write(f'    "low_severity": {summary["low_severity"]},\n')
            await f.write(f'    "total_findings": {summary["total_findings"]},\n')
            await f.write(f'    "average_confidence": {summary["average_confidence"]},\n')
            await f.write(f'    "risk_score": {summary["risk_score"]},\n')
            await f.write(f'    "categories": {json.dumps(summary["categories"])}\n')
            await f.write('  },\n')  # Added comma here
            if report.get("scan_duration_seconds") is not None:
                await f.write(f'  "scan_duration_seconds": {report["scan_duration_seconds"]},\n')
            await f.write(f'  "risk_assessment": {json.dumps(report["risk_assessment"])}\n')
            await f.write('}\n')
        if not quiet:
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
        if report.get('scan_duration_seconds') is not None:
            print(f"Scan Duration: {report['scan_duration_seconds']} seconds")
        print(f"Total Findings: {summary['total_findings']}")
        print()
        print("SEVERITY BREAKDOWN:")
        print(f"  High: {summary['high_severity']}")
        print(f"  Medium: {summary['medium_severity']}")
        print(f"  Low: {summary['low_severity']}")
        print()
        print("ANALYSIS METRICS:")
        print(f"  Average Confidence: {summary['average_confidence']:.3f}")
        print(f"  Risk Score: {summary['risk_score']:.2f}")
        print()
        print("CATEGORY BREAKDOWN:")
        for category, count in summary.get('categories', {}).items():
            print(f"  {category.replace('_', ' ').title()}: {count}")
        print()
        print(f"RISK ASSESSMENT: {report['risk_assessment']}")
        print(f"{'='*60}")
