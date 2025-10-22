import argparse
import importlib
import json
import os
import subprocess
import sys
import uuid
import ast
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from detectors.base import Detector

def validate_signal(signal):
    """Validate that a signal follows the required schema"""
    required_fields = ["id", "type", "detector_id", "file", "line", "column", "severity", "confidence", "detail", "context"]
    optional_fields = ["tags", "remediation", "evidence", "related_signals"]
    
    for field in required_fields:
        if field not in signal:
            print(f"Warning: Signal missing required field '{field}': {signal}")
            return False
    
    # Validate data types for important fields
    if not isinstance(signal["id"], str):
        print(f"Warning: Signal id must be string: {signal}")
        return False
    if not isinstance(signal["type"], str):
        print(f"Warning: Signal type must be string: {signal}")
        return False
    if not isinstance(signal["severity"], str) or signal["severity"] not in ["critical", "high", "medium", "low", "info"]:
        print(f"Warning: Signal severity must be one of critical, high, medium, low, info: {signal}")
        return False
    if not isinstance(signal["confidence"], (int, float)) or not 0 <= signal["confidence"] <= 1:
        print(f"Warning: Signal confidence must be number between 0 and 1: {signal}")
        return False
    if not isinstance(signal["line"], int) or signal["line"] < 1:
        print(f"Warning: Signal line must be positive integer: {signal}")
        return False
    if not isinstance(signal["column"], int) or signal["column"] < 1:
        print(f"Warning: Signal column must be positive integer: {signal}")
        return False
    
    return True


def get_git_info(repo_path):
    try:
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=repo_path).decode('utf-8').strip()
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_path).decode('utf-8').strip()
        return commit_hash, branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

def load_ruleset(ruleset_file):
    if ruleset_file:
        with open(ruleset_file, 'r') as f:
            return yaml.safe_load(f)
    return None

def get_file_language(file_path):
    """Map file extensions to programming languages"""
    ext = os.path.splitext(file_path)[1].lower()
    lang_map = {
        '.js': 'javascript',
        '.ts': 'typescript',
        '.py': 'python',
        '.go': 'go',
        '.java': 'java',
        '.rs': 'rust',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.html': 'html',
        '.htm': 'html'
    }
    return lang_map.get(ext, 'unknown')

def get_git_tracked_files(repo_path):
    """Get list of files tracked by git, which automatically respects .gitignore"""
    try:
        # Check if this is a git repository
        subprocess.check_output(['git', 'rev-parse', '--git-dir'], cwd=repo_path, stderr=subprocess.DEVNULL)

        # Get all tracked files using git ls-files
        result = subprocess.check_output(['git', 'ls-files'], cwd=repo_path, stderr=subprocess.DEVNULL)
        files = result.decode('utf-8').strip().split('')

    # Convert relative paths to absolute paths
        return [os.path.join(repo_path, f) for f in files if f.strip()]

    except (subprocess.CalledProcessError, FileNotFoundError):
    # Not a git repository or git not available, return None to fallback to os.walk()
        return None

def load_gitignore_patterns(repo_path):
    """Load gitignore patterns from .gitignore file if it exists (fallback for non-git repos)"""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
                return PathSpec.from_lines('gitwildmatch', patterns)
        except Exception as e:
            # If we can't read .gitignore, just continue without it
            print(f"Warning: Could not read .gitignore: {e}")
            pass
    return None

def load_detectors(ruleset):
    detectors = []
    default_ruleset = load_ruleset("rulesets/default.yaml")

    for file in os.listdir("detectors"):
        if file.endswith(".py") and file != "base.py" and file != "__init__.py":
            module_name = f"detectors.{file[:-3]}"
            module = importlib.import_module(module_name)
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, Detector) and obj is not Detector:
                    config = {}
                    # Load default config first
                    if default_ruleset and 'detectors' in default_ruleset:
                        for detector_config in default_ruleset['detectors']:
                            if detector_config['id'] == obj.id:
                                config.update(detector_config)
                                break

                    # Override with custom ruleset config
                    if ruleset and 'detectors' in ruleset:
                        for detector_config in ruleset['detectors']:
                            if detector_config['id'] == obj.id:
                                config.update(detector_config)
                                break

                    detectors.append(obj(config=config))
    return detectors

def setup_logging(verbose):
    """Setup logging based on verbosity level"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('network-mapper.log', mode='w')
        ]
    )

def main():
    parser = argparse.ArgumentParser(
        description='Network Mapper - Scan repositories for network activity',
        epilog='Examples:\n'
               '  python main.py /path/to/repo\n'
               '  python main.py scan --repo /path/to/repo --verbose'
    )
    parser.add_argument('repo_or_command', help='path to repository root, or "scan" command')
    parser.add_argument('repo', nargs='?', help='path to repository root (if using scan command)')
    parser.add_argument('--repo', dest='repo_flag', help='path to repository root (alternative to positional)')
    parser.add_argument('--output', default='output.json', help='output path (defaults to output.json)')
    parser.add_argument('--format', choices=['json', 'sarif', 'table'], default='json', help='output format')
    parser.add_argument('--ruleset', help='custom ruleset file')
    parser.add_argument('--languages', help='limit scanning to languages (comma-separated)')
    parser.add_argument('--threads', type=int, default=4, help='concurrency level')
    parser.add_argument('--include', action='append', help='include glob patterns')
    parser.add_argument('--exclude', action='append', help='exclude glob patterns')
    parser.add_argument('--git', action='store_true', default=True, help='gather git metadata (default: true)')
    parser.add_argument('--no-git', action='store_false', dest='git', help='disable git metadata gathering')
    parser.add_argument('--fail-on', choices=['critical', 'high', 'medium', 'low', 'info'], help='exit with non-zero if found severity >= value')
    parser.add_argument('--max-files', type=int, help='early stop threshold for large repos')
    parser.add_argument('--cache', help='cache ASTs between runs for faster repeated scans')
    parser.add_argument('--profile', action='store_true', help='enable run profiling for performance tuning')
    parser.add_argument('--verbose', '-v', action='store_true', help='enable verbose output')

    # Custom argument parsing to handle both simple and advanced usage
    args = parser.parse_args()

    # Handle --repo flag (takes precedence)
    if args.repo_flag:
        args.repo = args.repo_flag
        args.command = 'scan'
    else:
        # Handle simple usage: python main.py repo_path
        if args.repo_or_command != 'scan' and not args.repo_or_command.startswith('--'):
            # Simple usage: first argument is repo path
            if args.repo is None:
                args.repo = args.repo_or_command
                args.command = 'scan'
            else:
                parser.error("too many positional arguments")
        else:
            # Advanced usage: python main.py scan repo_path
            args.command = args.repo_or_command if args.repo_or_command == 'scan' else 'scan'
            # args.repo should be set by positional argument

    # Validate that we have a repo
    if not args.repo:
        parser.error("repository path is required")
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info(f"Starting network mapper scan of {args.repo}")
    if args.threads > 1:
        logger.info(f"Using {args.threads} threads for parallel processing")

    # Collect git info if enabled
    try:
        if args.git:
            commit_hash, branch = get_git_info(args.repo)
        else:
            commit_hash, branch = None, None
    except Exception as e:
        logger.warning(f"Could not gather git info: {e}")
        commit_hash, branch = None, None

    try:
        ruleset = load_ruleset(args.ruleset)
    except Exception as e:
        logger.error(f"Error loading ruleset: {e}")
        sys.exit(1)

    report = {
        "repo": {
            "path": os.path.abspath(args.repo),
            "commit_hash": commit_hash,
            "branch": branch,
            "scan_date": datetime.utcnow().isoformat() + "Z",
        },
        "network_activity_summary": {
            "total_network_calls": 0,
            "external_endpoints_detected": 0,
            "local_ports_exposed": 0,
            "signals_by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
        },
        "signals": [],
        "metadata": {
            "scanner_version": "0.1.0",
            "detectors_loaded": [],
            "ruleset": args.ruleset or "rulesets/default.yaml",
        },
    }

    try:
        detectors = load_detectors(ruleset)
        report["metadata"]["detectors_loaded"] = [d.id for d in detectors]
        logger.info(f"Loaded {len(detectors)} detectors: {report['metadata']['detectors_loaded']}")
    except Exception as e:
        logger.error(f"Error loading detectors: {e}")
        sys.exit(1)

    # Parse language filter if provided
    if args.languages:
        try:
            target_languages = [lang.strip() for lang in args.languages.split(',')]
            filtered_detectors = []
            for detector in detectors:
                # Only include detectors that support the specified languages
                if any(lang in target_languages for lang in detector.supported_languages):
                    filtered_detectors.append(detector)
            detectors = filtered_detectors
            logger.info(f"Filtered to {len(detectors)} detectors based on language filter: {target_languages}")
        except Exception as e:
            logger.error(f"Error filtering detectors by language: {e}")
            sys.exit(1)

    # Load gitignore patterns
    gitignore_spec = load_gitignore_patterns(args.repo)

    # Collect all files to process
    all_files = []
    try:
        for root, _, files in os.walk(args.repo):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, args.repo)

                # Check if file matches gitignore patterns
                should_exclude = False
                if gitignore_spec and gitignore_spec.match_file(rel_path):
                    should_exclude = True
                    continue

                # Check exclude patterns
                if args.exclude:
                    for pattern in args.exclude:
                        if pattern in rel_path:
                            should_exclude = True
                            break

                # Check include patterns
                if args.include:
                    should_include = False
                    for pattern in args.include:
                        if pattern in rel_path:
                            should_include = True
                            break
                    if not should_include:
                        should_exclude = True

                if not should_exclude:
                    all_files.append(file_path)
        
        # Limit files if max_files is set
        if args.max_files:
            all_files = all_files[:args.max_files]
        
        logger.info(f"Found {len(all_files)} files to scan")
    except Exception as e:
        logger.error(f"Error walking repository: {e}")
        sys.exit(1)
    
    # Process files in parallel
    def process_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            # Could not read this file, return empty list
            if args.verbose:
                logger.debug(f"Could not read file {file_path}: {e}")
            return []
        
        # Parse AST if the file is a supported language
        ast_obj = None
        file_lang = get_file_language(file_path)
        
        if file_lang == 'python':
            try:
                ast_obj = ast.parse(content)
            except SyntaxError as e:
                # Invalid Python syntax, continue with no AST
                if args.verbose:
                    logger.debug(f"Syntax error parsing Python file {file_path}: {e}")
                ast_obj = None
        # Add other language AST parsers as needed
        
        # Process with detectors that support this language
        file_signals = []
        for detector in detectors:
            if detector.config.get('enabled', True) is False:
                continue
            # Check if detector supports this language
            if file_lang in detector.supported_languages or not detector.supported_languages:
                try:
                    for signal in detector.match(file_path, content, ast_obj):
                        # Validate the signal before adding it
                        if validate_signal(signal):
                            file_signals.append(signal)
                        else:
                            if args.verbose:
                                logger.warning(f"Skipping invalid signal from {detector.id}: {signal}")
                except Exception as e:
                    logger.error(f"Error in detector {detector.id} for file {file_path}: {e}")
        
        return file_signals
    
    # Execute file processing in parallel
    all_signals = []
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Submit all files for processing
            future_to_file = {executor.submit(process_file, file_path): file_path for file_path in all_files}
            
            # Collect results as they complete
            completed_count = 0
            for future in as_completed(future_to_file):
                try:
                    file_signals = future.result()
                    all_signals.extend(file_signals)
                    completed_count += 1
                    
                    if completed_count % 100 == 0:  # Log progress every 100 files
                        logger.info(f"Processed {completed_count}/{len(all_files)} files...")
                        
                except Exception as e:
                    file_path = future_to_file[future]
                    logger.error(f"Error processing file {file_path}: {e}")
        
        logger.info(f"Scan completed. Found {len(all_signals)} signals across {len(all_files)} files.")
    except Exception as e:
        logger.error(f"Error during parallel processing: {e}")
        sys.exit(1)
    
    # Add all collected signals to the report
    report["signals"].extend(all_signals)

    # Update summary
    for signal in report["signals"]:
        if signal["type"] == "hardcoded_url":
            report["network_activity_summary"]["total_network_calls"] += 1
            report["network_activity_summary"]["external_endpoints_detected"] += 1
        elif signal["type"] == "port_exposure":
            report["network_activity_summary"]["local_ports_exposed"] += 1
        elif signal["type"] == "http_call":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "websocket_usage":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "raw_socket_usage":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "env_endpoint":
            report["network_activity_summary"]["external_endpoints_detected"] += 1
        elif signal["type"] == "certificate_check":
            pass # Handled by severity
        elif signal["type"] == "local_ip":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "cors_policy":
            pass # Handled by severity
        elif signal["type"] == "grpc_usage":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "third_party_sdk_usage":
            pass # Handled by severity
        elif signal["type"] == "asset_load":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "database_connection":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "cloud_sdk_usage":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "email_connection":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "dns_lookup":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "graphql_call":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "ftp_connection":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "web_scraping":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "oauth_flow":
            report["network_activity_summary"]["total_network_calls"] += 1
        elif signal["type"] == "realtime_connection":
            report["network_activity_summary"]["total_network_calls"] += 1

        report["network_activity_summary"]["signals_by_severity"][signal["severity"]] += 1

    # Handle different output formats
    try:
        if args.format == 'json':
            output_data = json.dumps(report, indent=2)
        elif args.format == 'sarif':
            # Convert to SARIF format (placeholder - would require actual SARIF implementation)
            output_data = json.dumps(report, indent=2)  # Placeholder
        elif args.format == 'table':
            # Format as a human-readable table (placeholder - would require pretty table implementation)
            output_data = json.dumps(report, indent=2)  # Placeholder
        else:
            output_data = json.dumps(report, indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_data)
            logger.info(f"Report written to {args.output}")
        else:
            print(output_data)
    except Exception as e:
        logger.error(f"Error writing output: {e}")
        sys.exit(1)

    # Check if we should fail based on severity threshold
    if args.fail_on:
        severity_order = ["info", "low", "medium", "high", "critical"]
        fail_idx = severity_order.index(args.fail_on)
        
        for severity, count in report["network_activity_summary"]["signals_by_severity"].items():
            if count > 0 and severity_order.index(severity) >= fail_idx:
                logger.error(f"Exiting with code 1 due to {count} {severity} severity signals found")
                sys.exit(1)
if __name__ == '__main__':
    main()
