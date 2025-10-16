#!/usr/bin/env python3
"""Core orchestrator for the DB Mapper scanning process."""

from pathlib import Path
from typing import List, Dict, Any
import json
import concurrent.futures
import threading

from .scanner import discover_files
from .detectors import run_detectors
from .cross_references import analyze_cross_references
from .risk_scorer import calculate_risk_scores
from .output import write_outputs


def run_scan(args) -> None:
    """Run the full scanning process.

    Args:
        args: Parsed command-line arguments
    """
    repo_path = args.path
    output_path = args.output
    formats = args.formats
    min_confidence = args.min_confidence
    include_patterns = args.include or ["**/*"]
    exclude_patterns = args.exclude or []
    languages = args.languages
    threads = args.threads

    print(f"Starting scan of {repo_path}")

    # 1. Discover files
    files = discover_files(repo_path, include_patterns, exclude_patterns, languages)
    print(f"Discovered {len(files)} files to scan")

    # 2. Run detectors
    findings = run_detectors(files, threads)
    print(f"Found {len(findings)} raw findings")

    # 3. Analyze cross-references
    findings_with_refs = analyze_cross_references(findings)
    print(f"Enhanced with cross-reference analysis")

    # 4. Calculate risk scores
    context = {
        "environment": "development",  # Could be made configurable
        "is_public_repo": False  # Could be detected
    }
    findings_with_risks = calculate_risk_scores(findings_with_refs, context)
    print(f"Calculated risk scores for {len(findings_with_risks)} findings")

    # 5. Filter by confidence
    filtered_findings = [f for f in findings_with_risks if f.get("confidence", 0) >= min_confidence]
    print(f"Filtered to {len(filtered_findings)} findings above confidence {min_confidence}")

    # 6. Prepare summary with severity counts
    severity_counts = {}
    for finding in filtered_findings:
        severity = finding.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    summary = {
        "files_scanned": len(files),
        "findings": len(filtered_findings),
        "severity_breakdown": severity_counts,
    }

    results = {
        "summary": summary,
        "findings": filtered_findings,
    }

    # 7. Write outputs
    write_outputs(results, output_path, formats)

    print(f"Scan complete. Results written to {output_path}")



