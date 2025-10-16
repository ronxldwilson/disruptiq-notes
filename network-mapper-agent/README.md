# Network Mapper — Code-Level Network Activity Scanner

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/)

## Table of Contents

1. [Project Summary](#project-summary)
2. [Installation & Quick Start](#installation--quick-start)
3. [Design Goals & Non-Goals](#design-goals--non-goals)
4. [Key Concepts & Terminology](#key-concepts--terminology)
5. [High-Level Architecture](#high-level-architecture)
6. [Core Features & Detector Catalog](#core-features--detector-catalog)
7. [Signal & JSON Report Schema (detailed)](#signal--json-report-schema-detailed)
8. [Sample Output (expanded)]#sample-output-expanded)
9. [Plugin / Detector API (spec)](#plugin--detector-api-spec)
10. [Language Parsers & Heuristics](#language-parsers--heuristics)
11. [Ruleset Format & Examples (YAML/JSON)](#ruleset-format--examples-yamljson)
12. [CLI Specification & Usage](#cli-specification--usage)
13. [CI/CD Integration & Automation](#cicd-integration--automation)
14. [Testing Strategy & Test Cases](#testing-strategy--test-cases)
15. [Performance & Scalability Considerations](#performance--scalability-considerations)
16. [Security & Privacy Considerations](#security--privacy-considerations)
17. [Extensibility & Roadmap](#extensibility--roadmap)
18. [Developer Guide: Adding a Detector](#developer-guide-adding-a-detector)

## Project Summary

**Network Mapper** is a static-analysis scanning tool focused on **network-related code artifacts** inside a repository. It examines source files, configuration, deployment manifests and scripts to detect:

* Outbound network calls (HTTP(S), WebSockets, gRPC, GraphQL, raw sockets, etc.)
* Inbound bindings and exposed ports (server.listen, socket.bind, container ports)
* CORS configurations and potential misconfigurations
* Hardcoded URLs, IPs, secrets or credentials used for network calls
* Environment variables, config files and templates that define endpoints
* Patterns in third-party libraries (e.g., axios, requests, fetch) and generated code

Output is a comprehensive JSON report with structured `signals`, metadata and summary statistics. The system is modular — detectors are pluggable, language parsers are separable, and rulesets are user-extensible.

**Primary consumers:** security teams, devops, SREs, compliance auditors, and developers who want to detect network exposure or unexpected external communications.

## Installation & Quick Start

### Prerequisites
- Python 3.7+
- Git (for repo metadata gathering)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-org/network-mapper.git
cd network-mapper

# Install dependencies
pip install -e .

# Or install directly from repository
pip install .
```

### Quick Start
```bash
# Basic scan
network-mapper scan --repo /path/to/your/repo

# Save output to file
network-mapper scan --repo /path/to/your/repo --output report.json

# Scan with custom ruleset
network-mapper scan --repo /path/to/your/repo --ruleset custom-rules.yaml --output report.json

# Scan specific languages only
network-mapper scan --repo /path/to/your/repo --languages javascript,python --output report.json

# Enable verbose output
network-mapper scan --repo /path/to/your/repo --verbose --output report.json

# Set failure threshold for CI/CD
network-mapper scan --repo /path/to/your/repo --fail-on high
```

---

# Design Goals & Non-Goals

## Goals

* **Accuracy-first:** use AST or parse-aware detection where possible; fall back to regex heuristics with context.
* **Extensible detectors:** drop-in detector modules with minimal bootstrapping.
* **Multi-language support:** initial support for JavaScript/TypeScript, Python, Go, Java, Rust, and basic YAML/JSON parsing for configs.
* **CI-friendly:** easily run as part of pre-merge checks and pipeline gates.
* **Actionable output:** precise file/line references, context snippets, severity, and remediation hints.
* **Offline-friendly:** local scanning with no telemetry by default.
* **Parallel processing:** multi-threaded scanning for performance on large codebases.

## Non-Goals (for v1)

* Dynamic runtime instrumentation or live network capture (not a runtime monitor).
* Complete coverage of every language or obscure framework (expandable later).
* Automated remediation / code modification (only detection & reporting).
* Ship large, language-specific parsers for every runtime in the initial release.

---

# Key Concepts & Terminology

* **Signal**: A single detection event (e.g., hardcoded URL, port listen, insecure CORS). Each signal includes type, severity, file, line, snippet and metadata.
* **Detector**: A modular component that analyzes file content (or AST) and emits `Signal` objects when it finds matches.
* **Scanner**: Orchestrates file traversal, language detection, parsing and detector execution.
* **Ruleset**: YAML/JSON file describing patterns, severities and meta for detectors. Enables user-defined detectors without code changes.
* **Reporter**: Aggregates signals, computes metadata (repo path, commit hash, scan time), and writes final JSON (or SARIF/other).
* **Heuristic**: A non-AST pattern (regex + context) used to detect network activity where AST is unavailable.

---

# High-Level Architecture

```
+-----------------+     +----------------+     +------------------+
|  File Walker    | --> | Language Parsers| --> | Detector Manager |
+-----------------+     +----------------+     +------------------+
        |                       |                      |
        v                       v                      v
   repo files             AST / tokens           Detectors (plugins)
        |                       |                      |
        +-----------------------+----------------------+
                                |
                            Scanner Core
                                |
                          Reporter / Writer
                                |
                      JSON / SARIF / Human Table
```

Components:

* **File Walker**: Walks repo, filters by patterns, respects `.gitignore`, optional `--include`/`--exclude`.
* **Language Parsers**: Returns AST or tokens for supported language; for unsupported languages provides raw text to heuristics.
* **Detector Manager**: Loads detectors dynamically, manages rulesets, runs detectors in parallel safely.
* **Reporter**: Aggregates and serializes outputs into canonical JSON.

---

# Core Features & Detector Catalog

## Core Features

* Multi-language scanning (AST-based where possible)
* Detector plugin system (auto-discovery)
* Configurable rulesets (default + user overrides)
* Severity tagging and remediation hints
* Output formats: JSON (canonical), SARIF (optional), and pretty CLI table
* Git metadata extraction (commit hash, branch)
* CI hooks: fail build on threshold or on specific severities
* Parallel processing with configurable thread count
* File filtering with include/exclude glob patterns
* Language-specific filtering
* Schema validation for all signals
* Comprehensive error handling and logging
* Progress tracking and verbose output

## Detector Catalog (starter)

* **HardcodedUrlDetector**: Finds direct `http(s)://` strings in code and config.
* **HttpCallDetector**: Detects `fetch`, `axios`, `requests.get`, `http.client`, `net/http` client usage and records endpoint expressions.
* **WebSocketDetector**: Finds `new WebSocket`, `ws.connect`, or `socket.io` client usage.
* **PortExposureDetector**: Detects `listen(port)`, `app.listen`, `server.bind`, docker-compose `ports`, Kubernetes `containerPort`.
* **CorsPolicyDetector**: Looks for `cors({origin: '*'})`, permissive CORS middlewares or wildcard configs.
* **RawSocketDetector**: Detects direct socket usage (Python `socket`, Node `net.Socket`).
* **GrpcDetector**: Detects gRPC client/server patterns in supported languages.
* **EnvEndpointDetector**: Finds env vars typically used for endpoints (e.g., `API_URL`, `SERVICE_ENDPOINT`) and whether defaults are insecure.
* **CertificateCheckDetector**: Detects disabling of certificate verification (`verify=False`, `rejectUnauthorized: false`).
* **LocalIpDetector**: Detects hardcoded local or private IPs (10.x.x.x, 192.168.x.x, 172.16-31).
* **ThirdPartySdkDetector**: Heuristics to spot usage of analytics/telemetry libs (e.g., `segment`, `mixpanel`) and suggest privacy implications.

Each detector includes rich metadata: `id`, `name`, `description`, `supported_languages`, `severity`, `default_enabled`, `tags`, `remediation`, `evidence`, and contextual information including pre/post snippets.

---

# Signal & JSON Report Schema (detailed)

Below is the canonical JSON structure the tool will output. **Make sure to validate against this schema** in the reporter.

```json
{
  "repo": {
    "path": "<absolute or supplied path>",
    "commit_hash": "<git commit sha>",
    "branch": "<git branch>",
    "scan_date": "YYYY-MM-DDTHH:MM:SSZ"
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
      "info": 0
    }
  },
  "signals": [
    {
      "id": "UUID or deterministic id",
      "type": "hardcoded_url",
      "detector_id": "hardcoded_url_v1",
      "file": "src/app.js",
      "line": 42,
      "column": 12,
      "severity": "medium",
      "confidence": 0.86,
      "detail": "Detected hardcoded external URL: https://analytics.badtracker.com",
      "context": {
        "snippet": "fetch('https://analytics.badtracker.com/event')",
        "pre": "  const req = getRequest();",
        "post": "  send(req);",
        "ast_path": ["CallExpression", "Argument[0]"]
      },
      "tags": ["external", "analytics"],
      "remediation": "Replace with env var process.env.ANALYTICS_URL or use internal proxy",
      "evidence": {
        "match": "https://analytics.badtracker.com/event",
        "regex": "https?://[\\w.-/:]+",
        "ast_node": { "type": "Literal", "value": "https://analytics.badtracker.com/event" }
      },
      "related_signals": ["signal-uuid-12", "signal-uuid-13"]
    }
    /* more signals... */
  ],
  "metadata": {
    "scanner_version": "0.1.0",
    "detectors_loaded": ["hardcoded_url_v1", "socket_usage_v1", "cors_v1"],
    "ruleset": "rulesets/default.yaml"
  }
}
```

### Field notes

* `confidence`: float 0–1; detectors should estimate confidence when using heuristics.
* `severity`: one of `critical`, `high`, `medium`, `low`, `info`.
* `ast_path`: optional path to AST location, helpers for later tooling to highlight code.
* `related_signals`: link signals that belong to the same service/flow (optional; generated by post-processing).
* `evidence.ast_node`: include the serialized AST node if AST-based detection used (trim to reasonable size).

---

# Sample Output (expanded)

Expanded example with multiple signals and metadata:

```json
{
  "repo": {
    "path": "/home/dev/projects/api-server",
    "commit_hash": "adf39c1",
    "branch": "feature/network-map",
    "scan_date": "2025-10-14T19:05:00Z"
  },
  "network_activity_summary": {
    "total_network_calls": 12,
    "external_endpoints_detected": 6,
    "local_ports_exposed": 2,
    "signals_by_severity": {
      "critical": 1,
      "high": 3,
      "medium": 5,
      "low": 2,
      "info": 1
    }
  },
  "signals": [
    {
      "id": "sig-0001",
      "type": "port_exposure",
      "detector_id": "port_exposure_v1",
      "file": "server.js",
      "line": 10,
      "column": 5,
      "severity": "high",
      "confidence": 0.95,
      "detail": "Server binds to port 8080 without TLS",
      "context": {
        "snippet": "app.listen(8080)",
        "pre": "const app = express();",
        "post": "console.log('Listening...');"
      },
      "tags": ["exposed", "http", "server"],
      "remediation": "Enable TLS or proxy behind reverse-proxy with TLS. Avoid binding insecure port in production.",
      "evidence": {
        "match": "listen\\((\\d+)\\)",
        "match_groups": { "1": "8080" }
      }
    },
    {
      "id": "sig-0002",
      "type": "hardcoded_url",
      "detector_id": "hardcoded_url_v1",
      "file": "src/app.js",
      "line": 42,
      "column": 18,
      "severity": "medium",
      "confidence": 0.88,
      "detail": "Detected hardcoded external URL: https://analytics.badtracker.com",
      "context": {
        "snippet": "fetch('https://analytics.badtracker.com/event')",
        "pre": "function track() {",
        "post": "}"
      },
      "tags": ["external", "analytics"],
      "remediation": "Use a configurable env var or internal tracking proxy.",
      "evidence": {
        "match": "https://analytics.badtracker.com/event"
      },
      "related_signals": ["sig-0005"]
    },
    {
      "id": "sig-0003",
      "type": "socket_usage",
      "detector_id": "raw_socket_v1",
      "file": "sockets/socket_client.py",
      "line": 12,
      "column": 3,
      "severity": "medium",
      "confidence": 0.9,
      "detail": "Detected raw socket connection to 10.0.0.12:9000",
      "context": {
        "snippet": "s.connect(('10.0.0.12', 9000))",
        "pre": "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)",
        "post": "s.send(data)"
      },
      "tags": ["internal", "raw-socket"],
      "remediation": "Avoid raw ip connections; use service discovery or env-based endpoints."
    }
    /* ...more signals... */
  ],
  "metadata": {
    "scanner_version": "0.2.0",
    "detectors_loaded": ["hardcoded_url_v1", "port_exposure_v1", "raw_socket_v1", "cors_v1"],
    "ruleset": "rulesets/default.yaml"
  }
}
```

---

# Plugin / Detector API (spec)

Detectors must be small, testable modules. The scanner will dynamically load them (via plugin discovery or registration). Below is an illustrative Python interface; adapt to your language of choice.

```python
# detectors/base.py
from typing import List, Dict, Any, Iterable
class Signal(Dict):
    pass

class Detector:
    id: str  # e.g., "hardcoded_url_v1"
    name: str
    description: str
    supported_languages: List[str] = []
    default_severity: str = "medium"

    def __init__(self, config: Dict[str, Any]):
        """Load config (ruleset overrides, thresholds, enabled flag)"""
        self.config = config

    def match(self, file_path: str, file_content: str, ast: Any = None) -> Iterable[Signal]:
        """
        Analyze file (and AST if provided) and yield Signal dicts.
        Each Signal must follow the canonical schema (file, line, severity, detail, etc.)
        """
        raise NotImplementedError()
```

## Plugin discovery

* Place detectors in `detectors/` folder.
* Use entry points or a simple file-based manifest `detectors/__init__.py` that lists available detectors.
* The scanner loads detectors and calls `match()` per file (for performance, call only detectors that support file language).

## Best practices for detectors

* Keep side-effects out of detectors (pure functions).
* Return multiple signals where necessary.
* Provide deterministic IDs (hash of file+line+match) so signals can be de-duped across runs.
* Include `confidence` and `evidence` in outputs.

---

# Language Parsers & Heuristics

## Recommended parsing approach

* **AST-first**: Use language-native ASTs for JavaScript (Esprima / @babel/parser), Python (`ast`), Go (`go/ast`), Java (javaparser), Rust (syn or tree-sitter). AST detection reduces false positives vs regex.
* **Fallback heuristics**: For templates, Dockerfiles, or unsupported languages, use regex heuristics plus contextual checks.
* **Tree-sitter**: Consider using tree-sitter for multi-language parsing with a common interface.
* **Currently implemented**: Python AST parsing with the built-in `ast` module. JavaScript parsing through regex with context-awareness.

## Example AST heuristics

* JavaScript: `CallExpression` where `callee.name` in (`fetch`, `axios`, `http.get`) and argument is a `Literal` or `TemplateLiteral` containing `http`.
* Python: `ast.Call` where `func.attr` in (`get`, `post`) and module name is `requests` or `http`.
* Ports: find `CallExpression` or `Call` nodes where function name contains `listen`, `bind`, `serve` with a numeric literal parameter.

## Heuristic patterns (starter)

* URL regex: `https?://[\w\.-/:?=&%+#]+`
* IP regex: `\b(?:\d{1,3}\.){3}\d{1,3}\b`
* Port listen: `(listen|serve|bind)\s*\(\s*(\d{2,5})\s*\)`
* CORS permissive: `cors\(\s*{[^}]*origin\s*:\s*['"]\*\s*['"]\s*}\s*\)`

---

# Ruleset Format & Examples (YAML/JSON)

Rulesets let users tune detection thresholds, severities and add custom regex-based detectors.

## rulesets/default.yaml (example)

```yaml
detectors:
  - id: hardcoded_url_v1
    enabled: true
    severity: medium
    languages: ["javascript", "python", "go"]
    regex: "https?://[\\w\\.-/:?=&%+#]+"
    explanation: "Detects hardcoded endpoint strings."

  - id: port_exposure_v1
    enabled: true
    severity: high
    languages: ["javascript", "python", "go"]
    regex: "(listen|bind|serve)\\s*\\(\\s*(\\d{2,5})\\s*\\)"
    conditions:
      - ensure_not_dev_only: true
    explanation: "Server appears to bind to a port"
```

## User overrides

* Support `--ruleset path/to/custom.yaml` to load/merge rules.
* Merge strategy: user-specified overrides default keys; unknown detectors may be added.

---

# CLI Specification & Usage

## Install & run (example)

```bash
# install (example)
pip install -e .

# basic scan
network-mapper scan --repo ./my-app --output ./reports/network-map.json

# scan with custom ruleset and verbosity
network-mapper scan --repo ./my-app --ruleset ./rulesets/security.yaml --output ./reports/out.json --verbose
```

## CLI flags

* `scan` (command): scan the repo

  * `--repo` (required): path to repository root
  * `--output` (optional): output path (defaults to stdout)
  * `--format` (json|sarif|table): output format
  * `--ruleset` (path): custom ruleset file
  * `--languages` (list): limit scanning to languages (comma-separated)
  * `--threads` (int): concurrency level (default: 4)
  * `--include` / `--exclude` globs
  * `--git` (bool): gather git metadata (true by default if git available)
  * `--fail-on` (severity): exit with non-zero if found severity >= value (e.g., high)
  * `--max-files` (int): early stop threshold for large repos
  * `--cache` (path): cache ASTs between runs for faster repeated scans
  * `--profile` (bool): enable run profiling for performance tuning
  * `--verbose`, `-v` (bool): enable verbose output with detailed logging

## Output examples

* JSON (canonical)
* SARIF (for developer tools)
* Pretty CLI table (for local dev)

---

# CI/CD Integration & Automation

## GitHub Actions example (check step)

`.github/workflows/network-map.yml`:

```yaml
name: Network Map Scan
on: [pull_request]
jobs:
  network-map:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run network mapper
        run: |
          pip install -e .
          network-mapper scan --repo . --output ./reports/network-map.json --ruleset ./rulesets/security.yaml
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: network-map-report
          path: ./reports/network-map.json
      - name: Fail on high severity
        run: |
          if jq '.network_activity_summary.signals_by_severity.high > 0' ./reports/network-map.json | grep true; then
            echo "High severity signals found. Failing build."
            exit 1
          fi
```

## Suggested checks

* Fail pipeline when `critical` or `high` signals count > 0
* Post the report as a PR comment (summarize top 5 signals)
* Add a badge showing last scan status (pass/fail)

---

# Testing Strategy & Test Cases

## Unit tests (detectors)

* Each detector has unit tests with:

  * Positive cases (should detect)
  * Negative cases (should not)
  * Confidence score sanity checks
  * AST-based tests with small snippets
* Use pytest (or chosen framework) and include fixtures for AST nodes.

## Integration tests

* A sample `examples/` repo per language that contains known signals; run full scan and compare output to golden JSON.
* Regression tests for ruleset merging.

## Fuzz tests

* Random code snippets to measure false positive rate on heuristics.

## Test scenarios (starter list)

* JS: `fetch('https://bad.example')` → hardcoded_url
* Node: `app.listen(process.env.PORT || 8080)` → port_exposure (but lower severity if env var used)
* Python: `requests.get(API_URL)` with default `API_URL='http://localhost'` → env endpoint detection
* Docker-compose: `ports: - "8080:80"` → container port exposure
* CORS: `app.use(cors({ origin: '*' }))` → cors_policy high severity

---

# Performance & Scalability Considerations

* **Parallel file scanning**: process files concurrently with a thread/process pool; parsers may be CPU-bound. Implemented with ThreadPoolExecutor for configurable concurrency.
* **AST caching**: cache parsed ASTs between runs (localized cache keyed by file hash).
* **Selective detectors**: only run detectors that declare support for the file language; skip binary and large files.
* **Memory usage**: stream reporter output when signals run into millions (unlikely, but prepare).
* **Batching detectors**: detectors that share parsing results should be run in a single pass over AST to reduce repeated traversal cost.
* **Progress tracking**: log progress every 100 files to monitor scan progress on large repositories.

---

# Security & Privacy Considerations

* **Local-first by default**: do not send any repository code or findings to external servers.
* **Telemetry**: disabled by default; opt-in only, and fully documented.
* **Sensitive data**: detectors may find secrets — treat output reports with care. Consider redaction options or selective output (e.g., redact values but show evidence match patterns).
* **Execution safety**: never execute repository code. Scanning must be purely static.

---

# Extensibility & Roadmap

## Short-term

* Add deeper language AST integrations (Java, C#).
* SARIF output for IDE integrations.
* Add graph-building to visualize service endpoint relationships.

## Mid-term

* LLM-based summarization of top risks per scan (optional, offline).
* Correlation with dependency graph (SBOM) to attribute external calls to packages or code.
* Plugin marketplace for community detectors.

## Long-term

* Runtime companion that validates static detections at runtime (opt-in).
* UI for browsing reports and interaction (filtering, triage, and assign).

---

## Developer Guide: Adding a Detector (step-by-step)

1. Create a new detector file under `detectors/`, e.g., `detectors/my_detector.py`.
2. Implement a `Detector` subclass that defines `id`, `name`, `supported_languages`, and `match()` method.
3. Add unit tests in `tests/detectors/test_my_detector.py`.
4. Add entry to `rulesets/default.yaml` (optional).
5. Run `python main.py scan --repo .` and ensure new detector appears in `metadata.detectors_loaded`.

## Example detector skeleton (Python)

```python
# detectors/hardcoded_url.py
from detectors.base import Detector, Signal
import re

URL_RE = re.compile(r"https?://[\w\.-/:?=&%+#]+", re.IGNORECASE)

class HardcodedUrlDetector(Detector):
    id = "hardcoded_url_v1"
    name = "Hardcoded URL Detector"
    description = "Detects hardcoded URLs in string literals"
    supported_languages = ["javascript", "python", "go", "rust"]

    def match(self, file_path, file_content, ast=None):
        for m in URL_RE.finditer(file_content):
            # compute line/column
            start = m.start()
            line = file_content.count("\n", 0, start) + 1
            col = start - file_content.rfind("\n", 0, start)
            yield {
                "id": f"hardurl-{file_path}-{line}-{m.group(0)}",
                "type": "hardcoded_url",
                "detector_id": self.id,
                "file": file_path,
                "line": line,
                "column": col,
                "severity": self.config.get("severity", "medium"),
                "confidence": 0.9,
                "detail": f"Detected hardcoded external URL: {m.group(0)}",
                "context": {"snippet": file_content[max(0,start-40):start+40]}
            }
```

---

# Final Notes & Quickstart Checklist

* [ ] Choose initial languages to support (JS, Python, Go recommended)
* [ ] Implement scanner + file walker
* [ ] Implement 4–6 core detectors (Hardcoded URL, HTTP calls, Port exposure, CORS, Raw socket)
* [ ] Implement reporter with canonical JSON schema
* [ ] Add CLI and Git integration
* [ ] Add CI job to run scans on PRs
* [ ] Write unit + integration tests (examples folder)
* [ ] Document rulesets and plugin API
