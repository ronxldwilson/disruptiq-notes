import asyncio
import concurrent.futures
import multiprocessing
import time
from pathlib import Path
from typing import List

from config import Config
from scanner import Scanner
from analyzer import Analyzer
from reporter import Reporter
from cli import CLI
from findings import Finding

# Global flag to signal shutdown
shutdown_requested = False

class Orchestrator:
    def __init__(self):
        self.shutdown_requested = False

    async def run_analysis(self) -> None:
        """Main entry point for the analysis."""
        try:
            # Parse arguments
            args = CLI.parse_arguments()

            # Load config
            config = Config(args.config)
            CLI.configure_from_args(config, args)

            # Initialize components
            scanner = Scanner(config)
            analyzer = Analyzer(config)
            reporter = Reporter(config)
            reporter.shutdown_check = lambda: self.shutdown_requested

            # Start timing
            start_time = time.time()

            # Scan directory
            print(f"Scanning directory: {args.scan_path}")
            if args.incremental:
                print("Using incremental scanning - only checking changed files")
                files_to_scan = scanner.scan_directory_incremental(args.scan_path, args.cache_dir)
                print(f"Found {len(files_to_scan)} changed files to analyze")
            else:
                files_to_scan = scanner.scan_directory(args.scan_path)
                print(f"Found {len(files_to_scan)} files to analyze")

            # Analyze files in parallel
            await self._analyze_files_parallel(analyzer, reporter, files_to_scan)

            # Print final verbose analysis if requested
            if config.get("verbose"):
                total_findings = len(reporter.findings)
                print(f"Analysis complete: {total_findings} findings across {len(files_to_scan)} files")

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Check if shutdown was requested before generating report
            if self.shutdown_requested:
                print("Shutdown requested, aborting report generation.")
                return

            # Generate and write final report
            report = reporter.generate_report(args.scan_path, elapsed_time, len(files_to_scan))
            await reporter.write_report(report, is_final=True)
            reporter.print_summary(report)

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                print("Interrupted by user.")
                return
            else:
                print(f"Error: {e}")
                import sys
                sys.exit(1)

    async def _analyze_files_parallel(self, analyzer: Analyzer, reporter: Reporter, files_to_scan: List[Path]) -> None:
        """Analyze files in parallel using process pool."""
        total_findings = 0
        total_files = len(files_to_scan)
        completed = 0
        next_milestone = 10  # Start at 10%

        max_workers = min(64, max(8, multiprocessing.cpu_count() * 4))

        # Analyze files in parallel using processes for CPU-bound work
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(analyzer.analyze_file, file_path) for file_path in files_to_scan]

            try:
                for future in concurrent.futures.as_completed(futures):
                    try:
                        findings_data = future.result(timeout=30.0)
                        # Only print findings count if verbose mode is enabled
                        if hasattr(analyzer, 'config') and analyzer.config.get('verbose', False):
                            print(f"Received {len(findings_data)} findings data from child process")
                        # Convert dictionaries to Finding objects
                        findings = []
                        for data in findings_data:
                            finding = Finding(**data)
                            findings.append(finding)
                        reporter.add_findings(findings)
                        total_findings += len(findings)
                        completed += 1

                        percent = (completed / total_files) * 100
                        while percent >= next_milestone and next_milestone <= 100:
                            print(f"Progress: {completed}/{total_files} files processed ({next_milestone}%)")
                            next_milestone += 10

                        if completed == total_files and next_milestone <= 100:
                            print(f"Progress: {completed}/{total_files} files processed (100%)")

                    except concurrent.futures.TimeoutError:
                        print("Timeout waiting for analysis result. Cancelling remaining tasks...")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    except Exception as e:
                        print(f"Error analyzing file: {e}")
                        continue
            except KeyboardInterrupt:
                print("\nInterrupted by user. Cancelling remaining analysis tasks...")
                self.shutdown_requested = True
                executor.shutdown(wait=False, cancel_futures=True)
