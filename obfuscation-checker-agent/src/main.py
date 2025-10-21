#!/usr/bin/env python3

import argparse
import asyncio
import concurrent.futures
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from scanner import Scanner
from analyzer import Analyzer
from reporter import Reporter

async def main():
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

        # Start timing
        start_time = time.time()

        # Scan directory
        print(f"Scanning directory: {args.scan_path}")
        files_to_scan = scanner.scan_directory(args.scan_path)
        print(f"Found {len(files_to_scan)} files to analyze")

        # Analyze files in parallel
        def analyze_single_file(file_path):
            return analyzer.analyze_file(file_path)

        total_findings = 0
        total_files = len(files_to_scan)
        completed = 0
        next_milestone = 10  # Start at 10%



        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(analyze_single_file, file_path) for file_path in files_to_scan]

            for future in concurrent.futures.as_completed(futures):
                findings = future.result()
                reporter.add_findings(findings)
                total_findings += len(findings)
                completed += 1

                # Show progress at percentage milestones
                percent = (completed / total_files) * 100
                while percent >= next_milestone and next_milestone <= 100:
                    print(f"Progress: {completed}/{total_files} files processed ({next_milestone}%)")
                    next_milestone += 10

                # Ensure 100% is shown if not already
                if completed == total_files and next_milestone <= 100:
                    print(f"Progress: {completed}/{total_files} files processed (100%)")

        # Print final verbose analysis if requested
        if config.get("verbose"):
            print(f"Analysis complete: {total_findings} findings across {total_files} files")

        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Generate and write final report
        report = reporter.generate_report(args.scan_path, elapsed_time, len(files_to_scan))
        await reporter.write_report(report, is_final=True)

        reporter.print_summary(report)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
