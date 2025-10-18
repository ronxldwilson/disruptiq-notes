"""
Report generation for static analysis results.
"""

from typing import Dict, List, Any
import json
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """Generates comprehensive reports from analysis results."""

    def generate_report(self, results: List[Any], languages: List[str],
                       output_format: str = 'json') -> Dict[str, Any]:
        """Generate a comprehensive report from analysis results."""

        # Aggregate findings
        all_findings = []
        tool_summaries = {}
        total_errors = 0

        for result in results:
            tool_name = result.tool_name
            findings = result.findings
            errors = result.errors

            all_findings.extend(findings)
            total_errors += len(errors)

            tool_summaries[tool_name] = {
                'findings_count': len(findings),
                'errors_count': len(errors),
                'errors': errors
            }

        # Categorize findings by severity
        severity_counts = self._categorize_findings(all_findings)

        report = {
            'timestamp': datetime.now().isoformat(),
            'languages_analyzed': languages,
            'tools_used': list(tool_summaries.keys()),
            'summary': {
                'total_findings': len(all_findings),
                'total_errors': total_errors,
                'severity_breakdown': severity_counts
            },
            'tool_summaries': tool_summaries,
            'findings': all_findings
        }

        return report

    def _categorize_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize findings by severity."""
        severity_levels = ['critical', 'high', 'medium', 'low', 'info']
        counts = {level: 0 for level in severity_levels}

        for finding in findings:
            severity = finding.get('severity', 'medium').lower()
            if severity in counts:
                counts[severity] += 1
            else:
                counts['medium'] += 1  # default to medium

        return counts

    def save_report(self, report: Dict[str, Any], file_path: str, format: str = 'json'):
        """Save the report to a file."""
        path = Path(file_path)

        if format.lower() == 'json':
            with open(path, 'w') as f:
                json.dump(report, f, indent=2)
        elif format.lower() == 'html':
            html_content = self._generate_html_report(report)
            with open(path, 'w') as f:
                f.write(html_content)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """Generate HTML report."""
        report = result['report']
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Static Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .findings {{ margin-top: 20px; }}
                .finding {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; }}
                .critical {{ border-left: 5px solid #ff0000; }}
                .high {{ border-left: 5px solid #ff6600; }}
                .medium {{ border-left: 5px solid #ffcc00; }}
                .low {{ border-left: 5px solid #66ff66; }}
            </style>
        </head>
        <body>
            <h1>Static Analysis Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Languages:</strong> {', '.join(report['languages_analyzed'])}</p>
                <p><strong>Tools Used:</strong> {', '.join(report['tools_used'])}</p>
                <p><strong>Total Findings:</strong> {report['summary']['total_findings']}</p>
                <p><strong>Total Errors:</strong> {report['summary']['total_errors']}</p>
                <h3>Severity Breakdown:</h3>
                <ul>
        """

        for severity, count in report['summary']['severity_breakdown'].items():
            html += f"<li>{severity.capitalize()}: {count}</li>"

        html += """
                </ul>
            </div>
            <div class="findings">
                <h2>Findings</h2>
        """

        for finding in report['findings']:
            severity_class = finding.get('severity', 'medium').lower()
            html += f"""
                <div class="finding {severity_class}">
                    <h3>{finding.get('rule', 'Unknown Rule')}</h3>
                    <p><strong>File:</strong> {finding.get('file', 'Unknown')}</p>
                    <p><strong>Line:</strong> {finding.get('line', 'Unknown')}</p>
                    <p><strong>Severity:</strong> {finding.get('severity', 'medium').capitalize()}</p>
                    <p>{finding.get('message', '')}</p>
                </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        return html
