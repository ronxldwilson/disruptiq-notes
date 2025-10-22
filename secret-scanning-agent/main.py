#!/usr/bin/env python3

import sys
import os
import subprocess
import argparse
from pathlib import Path
from patterns import find_secrets_in_file

# External tools configuration
EXTERNAL_TOOLS = {
    'trufflehog': {
        'command': ['trufflehog', 'filesystem'],
        'args': ['--json'],
        'description': 'TruffleHog - Git history and filesystem scanning'
    },
    'gitleaks': {
        'command': ['gitleaks', 'detect'],
        'args': ['--report-format', 'json', '--report-path', '-'],
        'description': 'Gitleaks - Fast git repository scanning'
    },
    'detect-secrets': {
        'command': ['detect-secrets', 'scan'],
        'args': ['--all-files'],
        'description': 'Detect-Secrets - Code analysis tool'
    },
    'secretlint': {
        'command': ['secretlint'],
        'args': ['--format', 'json'],
        'description': 'Secretlint - Pluggable linting tool'
    }
}

def is_text_file(file_path):
    """Check if a file is likely a text file"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return False
        return True
    except:
        return False

def run_external_tool(tool_name, directory):
    """Run an external secret scanning tool"""
    if tool_name not in EXTERNAL_TOOLS:
        print(f"Unknown tool: {tool_name}")
        return []

    tool_config = EXTERNAL_TOOLS[tool_name]
    command = tool_config['command'] + tool_config['args']

    # Add directory argument
    if tool_name in ['trufflehog', 'gitleaks']:
        command.extend(['--source', directory])
    elif tool_name == 'detect-secrets':
        command.append(directory)
    elif tool_name == 'secretlint':
        command.append(directory)

    try:
        print(f"Running {tool_config['description']}...")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            # Parse output - for now, just return the stdout
            return result.stdout.strip()
        else:
            print(f"Error running {tool_name}: {result.stderr}")
            return []
    except FileNotFoundError:
        print(f"Tool '{tool_name}' not found. Please install it first.")
        return []
    except Exception as e:
        print(f"Error running {tool_name}: {e}")
        return []

def scan_directory(directory):
    """Scan a directory for potential secrets"""
    findings = []
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return findings

    print(f"Scanning: {directory}")

    # Find all files, excluding common binary extensions
    exclude_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
                         '.mp3', '.mp4', '.avi', '.mov', '.zip', '.tar', '.gz',
                         '.exe', '.dll', '.so', '.dylib', '.pyc', '.class'}

    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            if file_path.suffix.lower() in exclude_extensions:
                continue
            if not is_text_file(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    file_findings = find_secrets_in_file(str(file_path), content)
                    findings.extend(file_findings)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

    return findings

def main():
    parser = argparse.ArgumentParser(description='Secret Scanning Agent')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--tools', nargs='+', choices=list(EXTERNAL_TOOLS.keys()),
                       help='External tools to use (space-separated)')

    args = parser.parse_args()

    directory = args.directory
    tools = args.tools or []

    # Run built-in regex scan
    print("Running built-in regex scan...")
    findings = scan_directory(directory)

    # Run external tools
    external_outputs = []
    for tool in tools:
        output = run_external_tool(tool, directory)
        if output:
            external_outputs.append(f"\n--- {tool.upper()} OUTPUT ---\n{output}")

    # Display results
    if findings:
        print("\n--- BUILT-IN REGEX FINDINGS ---")
        for finding in findings:
            print(f"Found potential secret in {finding['file']}:{finding['line']} - {finding['type']}")
        total_findings = len(findings)
    else:
        total_findings = 0

    for output in external_outputs:
        print(output)
        # Note: External tool outputs are displayed as-is
        # In a full implementation, you'd parse and count them

    if total_findings > 0:
        print(f"\nBuilt-in scan found {total_findings} potential secrets.")
    else:
        print("\nBuilt-in scan found no potential secrets.")

if __name__ == "__main__":
    main()
