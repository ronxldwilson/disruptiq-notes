#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from scanner import Scanner
from analyzer import Analyzer
from reporter import Reporter

def main():
    parser = argparse.ArgumentParser(description="Obfuscation Checker Agent")
    parser.add_argument("scan_path", help="Path to the directory to scan")
    parser.add_argument("--config", help="Path to config file", default=None)
    parser.add_argument("--output", help="Output file for report", default=None)
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        # Load config
        config = Config(args.config)
        if args.output:
            config.set("output_file", args.output)
        if args.verbose:
            config.set("verbose", True)

        # Initialize components
        scanner = Scanner(config)
        analyzer = Analyzer(config)
        reporter = Reporter(config)

        # Scan directory
        print(f"Scanning directory: {args.scan_path}")
        files_to_scan = scanner.scan_directory(args.scan_path)
        print(f"Found {len(files_to_scan)} files to analyze")

        # Analyze files
        total_findings = 0
        for file_path in files_to_scan:
            if config.get("verbose"):
                print(f"Analyzing: {file_path}")
            findings = analyzer.analyze_file(file_path)
            reporter.add_findings(findings)
            total_findings += len(findings)

        # Generate and write report
        report = reporter.generate_report(args.scan_path)
        reporter.write_report(report)
        reporter.print_summary(report)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
