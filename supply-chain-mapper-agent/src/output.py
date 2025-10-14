import json
import os
from datetime import datetime

class OutputFormatter:
    def __init__(self):
        pass

    def generate_report(self, repo_path, dependencies, signals, commit_hash="unknown"):
        """
        Generate the final JSON report according to the specification
        """
        ecosystems_detected = list(set(dep["ecosystem"] for dep in dependencies))
        
        report = {
            "repo": {
                "path": os.path.abspath(repo_path),
                "commit_hash": commit_hash,
                "scan_date": datetime.utcnow().isoformat() + "Z"
            },
            "scan_summary": {
                "total_manifests": len(set(dep["manifest_path"] for dep in dependencies)),
                "ecosystems_detected": ecosystems_detected,
                "total_dependencies": len(dependencies),
                "total_signals": len(signals)
            },
            "dependencies": dependencies
        }
        
        return report

    def save_report(self, report, output_path):
        """
        Save the report to a JSON file
        """
        try:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving report to {output_path}: {e}")
            return False

    def print_summary(self, report):
        """
        Print a summary of the scan results to stdout
        """
        print(f"\nScan Summary:")
        print(f"- Repository: {report['repo']['path']}")
        print(f"- Commit: {report['repo']['commit_hash']}")
        print(f"- Scan Date: {report['repo']['scan_date']}")
        print(f"- Total Dependencies: {report['scan_summary']['total_dependencies']}")
        print(f"- Total Manifests: {report['scan_summary']['total_manifests']}")
        print(f"- Ecosystems Detected: {', '.join(report['scan_summary']['ecosystems_detected'])}")
        print(f"- Total Risk Signals: {report['scan_summary']['total_signals']}")
        
        # Breakdown by ecosystem
        print(f"\nDependencies by Ecosystem:")
        for ecosystem in report['scan_summary']['ecosystems_detected']:
            count = len([dep for dep in report['dependencies'] if dep['ecosystem'] == ecosystem])
            print(f"  - {ecosystem}: {count} dependencies")