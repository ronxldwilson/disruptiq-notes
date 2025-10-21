# Network Mapper Agent

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)

## Overview

Network Mapper Agent is a static analysis tool that scans code repositories to detect network-related activities and potential security issues. It analyzes source code to identify hardcoded URLs, exposed ports, insecure configurations, and other network patterns that may indicate security concerns or architectural issues.

## Features

### Current Capabilities

- **Multi-language Support**: Currently supports JavaScript, Python, Go, Java, Rust, and YAML/JSON files
- **AST-based Analysis**: Uses Python AST parsing for accurate detection (regex fallback for other languages)
- **11 Built-in Detectors**:
  - Hardcoded URL detection
  - HTTP call detection (fetch, axios, requests)
  - Port exposure detection
  - WebSocket usage detection
  - CORS policy analysis
  - Raw socket usage detection
  - gRPC detection
  - Environment variable endpoint detection
  - Certificate verification bypass detection
  - Local/private IP detection
  - Third-party SDK usage detection

- **Flexible Output**: JSON reports with detailed metadata and context
- **Parallel Processing**: Multi-threaded scanning for performance
- **Git Integration**: Automatic commit hash and branch detection, respects .gitignore patterns
- **Configurable Rulesets**: YAML-based detector configuration
- **CI/CD Integration**: Exit codes based on severity thresholds
- **Gitignore Support**: Automatically excludes files matching .gitignore patterns

## Installation

### Prerequisites
- Python 3.7+
- Git (optional, for metadata gathering)

### Install
```bash
# Clone the repository
git clone <repository-url>
cd network-mapper-agent

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# Or run directly (no installation needed)
python main.py /path/to/repo
```

## Quick Start

### Basic Usage
```bash
# Simple scan (recommended)
python main.py /path/to/your/repo

# Advanced scan with options
python main.py scan --repo /path/to/your/repo --verbose --output my-report.json

# Scan with custom ruleset
python main.py /path/to/your/repo --ruleset custom_ruleset.yaml

# Filter by languages
python main.py /path/to/your/repo --languages javascript,python

# Enable verbose logging
python main.py /path/to/your/repo --verbose
```

### Example Output
When run on the included examples, the tool produces a JSON report like this:

```json
{
  "repo": {
    "path": "/path/to/repo",
    "commit_hash": "abc123...",
    "branch": "main",
    "scan_date": "2025-10-21T09:07:08Z"
  },
  "network_activity_summary": {
    "total_network_calls": 13,
    "external_endpoints_detected": 8,
    "local_ports_exposed": 1,
    "signals_by_severity": {
      "critical": 0,
      "high": 3,
      "medium": 11,
      "low": 4,
      "info": 0
    }
  },
  "signals": [
    {
      "id": "hardurl-src/app.js-1-https://api.example.com",
      "type": "hardcoded_url",
      "detector_id": "hardcoded_url_v1",
      "file": "src/app.js",
      "line": 1,
      "column": 12,
      "severity": "medium",
      "confidence": 0.9,
      "detail": "Detected hardcoded external URL: https://api.example.com",
      "context": {
        "snippet": "axios.get('https://api.example.com/data')",
        "pre": "const axios = require('axios');",
        "post": ".then(response => {"
      },
      "tags": ["external", "url", "hardcoded"],
      "remediation": "Replace with env var process.env.API_URL or use internal proxy",
      "evidence": {
        "match": "https://api.example.com",
        "regex": "https?://[\\w\\.-/:?=&%+#]+"
      }
    }
  ],
  "metadata": {
    "scanner_version": "0.1.0",
    "detectors_loaded": ["hardcoded_url_v1", "http_call_v1", "port_exposure_v1", ...],
    "ruleset": "rulesets/default.yaml"
  }
}
```

## Architecture

### Core Components

- **Scanner Core** (`main.py`): Orchestrates file traversal (respects .gitignore), detector loading, and parallel processing
- **Detector System** (`detectors/`): Pluggable modules for different types of network activity detection
- **Ruleset System** (`rulesets/`): YAML configuration for detector behavior
- **Reporter**: Aggregates signals into structured JSON output

### Detector Interface

Each detector implements a simple interface:

```python
class MyDetector(Detector):
    id = "my_detector_v1"
    name = "My Custom Detector"
    description = "Detects specific network patterns"
    supported_languages = ["javascript", "python"]

    def match(self, file_path, file_content, ast=None):
        # Analyze file and yield Signal dictionaries
        yield {
            "type": "custom_signal",
            "severity": "medium",
            "detail": "Found something interesting",
            # ... other signal fields
        }
```

## Configuration

### Default Ruleset

The `rulesets/default.yaml` file controls detector behavior:

```yaml
detectors:
  - id: hardcoded_url_v1
    enabled: true
    severity: medium
    languages: ["javascript", "python", "go"]
    regex: "https?://[\\w\\.-/:?=&%+#]+"
    explanation: "Detects hardcoded endpoint strings."
```

### Custom Rulesets

Create custom rulesets to override defaults:

```bash
# Use custom ruleset
python main.py scan --repo . --ruleset my_rules.yaml
```

Example custom ruleset (`custom_ruleset.yaml`):
```yaml
detectors:
  - id: hardcoded_url_v1
    enabled: false  # Disable this detector
  - id: port_exposure_v1
    severity: critical  # Increase severity
```

## Command Line Options

```
usage: main.py [-h] [--output OUTPUT] [--format {json,sarif,table}]
               [--ruleset RULESET] [--languages LANGUAGES] [--threads THREADS]
               [--include INCLUDE] [--exclude EXCLUDE] [--git] [--no-git]
               [--fail-on {critical,high,medium,low,info}]
               [--max-files MAX_FILES] [--cache CACHE] [--profile] [--verbose]
               repo_or_command [repo]

Network Mapper - Scan repositories for network activity

positional arguments:
  repo_or_command       path to repository root, or "scan" command
  repo                  path to repository root (if using scan command)

options:
  -h, --help            show this help message and exit
  --repo REPO           path to repository root (alternative to positional)
  --output OUTPUT       output path (defaults to report.json)
  --format {json,sarif,table}
                        output format (sarif/table not implemented)
  --ruleset RULESET     custom ruleset file
  --languages LANGUAGES comma-separated list of languages to scan
  --threads THREADS     concurrency level (default: 4)
  --include INCLUDE     include glob patterns
  --exclude EXCLUDE     exclude glob patterns
  --git                 gather git metadata (default: true)
  --no-git              disable git metadata gathering
  --fail-on {critical,high,medium,low,info}
                        exit with non-zero if found severity >= value
  --max-files MAX_FILES early stop threshold for large repos
  --cache CACHE         cache ASTs between runs (not implemented)
  --profile             enable run profiling (not implemented)
  --verbose, -v         enable verbose output

Examples:
  python main.py /path/to/repo                    # Scan with automatic .gitignore support
  python main.py scan --repo /path/to/repo --verbose
```

## Detectors

### Available Detectors

| Detector | Description | Severity | Languages |
|----------|-------------|----------|-----------|
| hardcoded_url_v1 | Detects hardcoded URLs in strings | medium | js, py, go, rust |
| http_call_v1 | Detects HTTP library usage | medium | js, py |
| port_exposure_v1 | Detects server port binding | high | js, py, go |
| websocket_v1 | Detects WebSocket usage | medium | js |
| cors_policy_v1 | Detects permissive CORS settings | high | js |
| raw_socket_v1 | Detects raw socket usage | medium | py, js |
| grpc_v1 | Detects gRPC usage | medium | all |
| env_endpoint_v1 | Detects environment-based endpoints | low | js, py |
| certificate_check_v1 | Detects certificate verification bypass | high | py, js |
| local_ip_v1 | Detects hardcoded private IPs | low | all |
| third_party_sdk_v1 | Detects telemetry/analytics SDKs | medium | js, py |

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/detectors/test_hardcoded_url.py
```

### Adding a Detector

1. Create `detectors/new_detector.py`
2. Implement the `Detector` interface
3. Add unit tests in `tests/detectors/test_new_detector.py`
4. Update `rulesets/default.yaml` if needed

### Project Structure
```
network-mapper-agent/
├── main.py                 # Main scanner application
├── detectors/              # Detector implementations
│   ├── base.py            # Base detector class
│   ├── hardcoded_url.py   # URL detection
│   └── ...                # Other detectors
├── rulesets/              # Configuration files
│   └── default.yaml       # Default detector config
├── tests/                 # Unit tests
├── examples/              # Example code for testing
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Network Security Scan
on: [pull_request]

jobs:
  network-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run network mapper
        run: python main.py . --output network-report.json
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: network-scan-report
          path: network-report.json
      - name: Fail on high severity
        run: |
          python -c "
          import json
          with open('network-report.json') as f:
              report = json.load(f)
          if report['network_activity_summary']['signals_by_severity']['high'] > 0:
              print('High severity issues found')
              exit(1)
          "
```

## Limitations

### Current Limitations
- AST parsing only implemented for Python (regex-based detection for other languages)
- No SARIF or table output formats (JSON only)
- No caching mechanism implemented
- Limited language support for advanced features
- No advanced remediation suggestions

### Future Enhancements
- Full AST support for JavaScript, Go, Java, Rust
- Additional output formats (SARIF, HTML reports)
- Performance optimizations and caching
- Advanced ruleset features
- Integration with IDEs and code editors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
