# Secret Scanning Agent

## Overview

A simple secret scanning tool that scans directories for potential secrets like API keys, passwords, and tokens. It can integrate popular open-source secret scanning tools for enhanced detection.

## Features

- **Basic Regex Scanning**: Built-in patterns for common secrets
- **Multi-Tool Support**: Integrates with popular tools like TruffleHog and Gitleaks
- **Simple Usage**: Run with a single command
- **Configurable**: Easy to add custom patterns
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Supported Tools

The tool can integrate with popular secret scanning tools:

- **TruffleHog**: Git history scanning
- **Gitleaks**: Fast git repository scanning
- **Detect-Secrets**: Code analysis tool
- **Built-in Regex**: Basic pattern matching

## Installation

### Prerequisites

- Python 3.6+

### Installing External Tools (Optional)

The agent can use popular secret scanning tools for enhanced detection:

- **TruffleHog**: `pip install trufflehog` or download from https://github.com/trufflesecurity/trufflehog
- **Gitleaks**: Download from https://github.com/gitleaks/gitleaks/releases
- **Detect-Secrets**: `pip install detect-secrets`
- **Secretlint**: `npm install -g @secretlint/secretlint-rule-preset-recommend`

### Install

```bash
git clone https://github.com/your-org/secret-scanning-agent.git
cd secret-scanning-agent
pip install -r requirements.txt
```

## Usage

### Simple Scan

```bash
python main.py <directory_path>
```

Example:
```bash
python main.py /path/to/your/project
python main.py .
```

### With External Tools

If you have external tools installed, you can use them alongside the built-in scan:

```bash
python main.py /path/to/project --tools trufflehog gitleaks
```

Available tools: trufflehog, gitleaks, detect-secrets, secretlint

**Note**: External tools must be installed separately. The agent will run them and display their output.

## Output

The tool will print findings to the console, showing:
- File path
- Line number
- Type of secret found
- Matched pattern

When using external tools, their output will be displayed separately.

Example output:
```
Running built-in regex scan...
Scanning: /path/to/project
Found potential secret in file.py:10 - AWS Access Key

--- TRUFFLEHOG OUTPUT ---
[JSON output from TruffleHog]

--- GITLEAKS OUTPUT ---
[JSON output from Gitleaks]

Built-in scan found 1 potential secret.
```

## Security Notes

- Review all findings manually - there may be false positives
- This tool is not foolproof; use alongside manual reviews

## Development

To add new secret patterns, edit the `patterns.py` file.
