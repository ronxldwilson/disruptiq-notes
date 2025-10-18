# Static Analysis Agent 🚀

**Enterprise-Grade Multi-Language Code Analysis Platform**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tools](https://img.shields.io/badge/Tools-7+-orange.svg)]()

The Static Analysis Agent is a comprehensive, AI-powered platform that performs **enterprise-grade static analysis** across multiple programming languages. It autonomously analyzes codebases for security vulnerabilities, code quality issues, bugs, and best practices violations using industry-standard tools.

## ✨ Key Features

### 🔍 **Comprehensive Analysis**
- **7+ Specialized Tools**: Bandit, Flake8, Pylint, Semgrep, ESLint, Golint, Cppcheck
- **6 Programming Languages**: Python, JavaScript/TypeScript, Go, C/C++, Java, Ruby
- **Parallel Execution**: Runs tools simultaneously for maximum speed
- **Intelligent Detection**: Auto-detects languages and selects appropriate tools

### 🎯 **Security-First Approach**
- **Vulnerability Detection**: SQL injection, XSS, buffer overflows, command injection
- **Cryptography Validation**: Weak algorithms, insecure random usage
- **Access Control**: Path traversal, privilege escalation detection
- **OWASP Top 10**: Comprehensive coverage of web security issues

### 📊 **Rich Reporting**
- **Multiple Formats**: JSON (CI/CD), Markdown (docs), HTML (web), Summary (quick)
- **Severity Classification**: High/Medium/Low priority findings
- **Tool Integration**: Aggregated results from all tools
- **Historical Tracking**: Automatic report archiving

### ⚙️ **Enterprise Configuration**
- **YAML-Based Config**: Fully customizable tool settings
- **Environment-Specific**: Different configs for dev/staging/prod
- **CI/CD Ready**: JSON output perfect for automated pipelines
- **Hot Reloading**: Configuration changes without restart

### 🚀 **Performance Optimized**
- **Caching**: Results cached between runs
- **Selective Scanning**: Skip unchanged files
- **Resource Management**: Configurable concurrency limits
- **Timeout Protection**: Prevents hanging on large codebases

## 🏗️ Architecture

### Core Components

```
Static Analysis Agent
├── Agent Core          # Orchestration & decision making
├── Tool Registry       # Tool management & discovery
├── Analysis Engine     # Parallel execution & result processing
├── Report Generator    # Multi-format report creation
└── Configuration System # YAML-based settings management
```

### Analysis Workflow

1. **🔍 Codebase Discovery**: Auto-detect languages and project structure
2. **🎯 Tool Selection**: Intelligent tool selection based on languages
3. **⚡ Parallel Execution**: Run all tools simultaneously
4. **📊 Result Aggregation**: Normalize and prioritize findings
5. **📋 Report Generation**: Create comprehensive reports
6. **💾 Archive Management**: Automatic report versioning

### Data Flow

```
Codebase → Language Detection → Tool Selection → Parallel Analysis → Result Aggregation → Multi-Format Reports
```

## Supported Tools

### Currently Installed & Active

#### Security Analysis
- **✅ Bandit**: Security linter for Python code (Active)
- **✅ Semgrep**: Multi-language semantic code analysis for security vulnerabilities (Active)

#### Code Quality & Style
- **✅ Flake8**: Python style guide enforcement and error detection (Active)
- **✅ Pylint**: Python code analysis for bugs and quality (Active)
- **✅ ESLint**: JavaScript/TypeScript linting (Active)
- **✅ Golint**: Go code linting (Active)

### Available for Installation

#### Additional Code Quality
- **📦 Cppcheck**: C/C++ static analysis (Config ready, manual install required on Windows)
- **📦 RuboCop**: Ruby static code analyzer (Config ready, Ruby required)

#### Additional Security
- **Safety**: Checks Python dependencies for known security vulnerabilities
- **Trivy**: Comprehensive security scanner for vulnerabilities, secrets, and misconfigurations

#### Other Tools
- **SonarQube/SonarLint**: Multi-language code quality and security
- **Prettier**: Code formatting consistency checks

#### Dependency Analysis
- **OWASP Dependency-Check**: Identifies vulnerable dependencies
- **Snyk**: Security and license compliance for open-source dependencies

### Tool Status
- **✅ Active**: 6 tools currently installed and working
- **📦 Available**: 2 tools with configs ready (cppcheck, rubocop)
- **🔧 Configurable**: All tools support custom configuration via YAML files

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**: Core runtime
- **Node.js 14+**: Required for ESLint (JavaScript/TypeScript)
- **Go 1.16+**: Required for Golint (Go analysis)
- **Git**: Required for some tools

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd static-analysis-agent

# Install Python dependencies
pip install -r requirements.txt

# Install analysis tools (recommended)
python -m src install-tools
```

### Basic Usage

```bash
# Analyze entire codebase (auto-detects languages & tools)
python -m src analyze /path/to/your/project

# Analyze specific directory
python -m src analyze src/

# Analyze with custom report name
python -m src analyze my-app --report-name sprint-123-audit

# Get quick summary
python -m src analyze my-app --output-format summary
```

## 📖 Usage Guide

### Command Line Options

```bash
python -m src analyze [OPTIONS] CODEBASE_PATH

Options:
  -l, --languages TEXT            Specify programming languages to analyze
  -t, --tools TEXT                Specify tools to use (space-separated)
  -f, --output-format [json|html|markdown|summary]
                                  Output format (default: json)
  -d, --output-dir PATH           Output directory (default: output)
  -n, --report-name TEXT          Report filename (default: latest)
  -q, --quiet                     Suppress console output
  --help                          Show help message
```

### Advanced Examples

#### Development Workflow
```bash
# Quick security check during development
python -m src analyze . --tools bandit semgrep --output-format summary

# Full analysis before commit
python -m src analyze . --report-name pre-commit-check

# CI/CD integration
python -m src analyze . --output-format json --quiet
```

#### Language-Specific Analysis
```bash
# Python project analysis
python -m src analyze python-app --tools bandit flake8 pylint

# JavaScript/React analysis
python -m src analyze frontend --tools eslint semgrep

# Go microservice analysis
python -m src analyze backend --tools golint semgrep

# Multi-language monorepo
python -m src analyze .  # Auto-detects all languages
```

#### Report Management
```bash
# Custom report naming
python -m src analyze . --report-name security-audit-week-42

# Different output formats
python -m src analyze . --output-format markdown  # GitHub-friendly
python -m src analyze . --output-format html      # Web viewing
python -m src analyze . --output-format json      # CI/CD integration

# View previous reports
ls output/reports/    # Current reports
ls output/archives/   # Historical reports
```

#### Tool Management
```bash
# List all available tools
python -m src list-tools

# Install specific tools
python -m src install-tools --tool eslint
python -m src install-tools --tool golint

# Clean old archived reports
python -m src clean-reports --days 30
```

### Configuration Examples

#### CI/CD Pipeline Integration
```yaml
# .github/workflows/security.yml
name: Security Analysis
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Static Analysis
        run: |
          pip install -r requirements.txt
          python -m src analyze . --output-format json --quiet
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: output/reports/latest.json
```

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running static analysis..."
python -m src analyze . --output-format summary --quiet

if [ $? -ne 0 ]; then
    echo "Static analysis failed. Please fix issues before committing."
    exit 1
fi

echo "Static analysis passed!"
exit 0
```

#### Docker Integration
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs npm golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install analysis tools
RUN npm install -g eslint && \
    go install golang.org/x/lint/golint@latest

# Copy and setup application
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Run analysis
CMD ["python", "-m", "src", "analyze", ".", "--output-format", "json"]
```
# Specify languages to focus on
python -m src analyze /path/to/codebase --languages python,javascript

# Use specific tools
python -m src analyze /path/to/codebase --tools semgrep

# Generate HTML report
python -m src analyze /path/to/codebase --output-format html

# Save to custom directory
python -m src analyze /path/to/codebase --output-dir reports

# Quiet mode (no console output, only file)
python -m src analyze /path/to/codebase --quiet
```

## 📊 Report Formats

### JSON Format (CI/CD)
```json
{
  "success": true,
  "detected_languages": ["python", "javascript"],
  "tools_used": ["bandit", "flake8", "eslint"],
  "results": [...],
  "report": {
    "summary": {
      "total_findings": 25,
      "severity_breakdown": {"high": 3, "medium": 12, "low": 10}
    }
  }
}
```

### Markdown Format (Documentation)
```markdown
# Static Analysis Report

**Generated:** 2025-10-19T14:30:00

## Summary
- **Languages Analyzed:** python, javascript
- **Tools Used:** bandit, flake8, eslint
- **Total Findings:** 25

### Severity Breakdown
- **High:** 3
- **Medium:** 12
- **Low:** 10

## Tool Results
### bandit
- Findings: 8
- Errors: 0

### flake8
- Findings: 12
- Errors: 0
```

### Summary Format (Quick Review)
```
STATIC ANALYSIS SUMMARY REPORT
========================================
Generated: 2025-10-19T14:30:00

Languages: python, javascript
Tools: bandit, flake8, eslint
Total Findings: 25
Total Errors: 0

SEVERITY BREAKDOWN:
  HIGH: 3
  MEDIUM: 12
  LOW: 10

For detailed results, see the full JSON report.
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd static-analysis-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Adding New Tools

1. **Create tool class** in `src/tools/integrations/`
```python
# src/tools/integrations/newtool.py
from ..base_tool import BaseTool, AnalysisResult

class NewTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="newtool",
            description="Description of new tool",
            supported_languages=["python"]
        )

    async def install(self) -> bool:
        # Installation logic
        pass

    def is_installed(self) -> bool:
        # Check installation
        pass

    async def run(self, codebase_path, config) -> AnalysisResult:
        # Run analysis
        pass
```

2. **Add configuration** in `config/tools/newtool.yaml`
```yaml
enabled: false  # Initially disabled
# Tool-specific configuration options
```

3. **Update agent config** in `config/agent.yaml`
```yaml
enabled_tools:
  - newtool  # Add to list
```

4. **Update documentation** in `README.md` and `config/README.md`

### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_tool_integration.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Run static analysis on the agent itself
python -m src analyze src/ --tools flake8 pylint bandit

# Format code
black src/
isort src/

# Type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tool Authors**: Thanks to all the open-source tool maintainers
- **Contributors**: Community contributions welcome
- **Security Community**: For ongoing vulnerability research

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Full Docs](https://your-docs-site.com)

---

**Happy Analyzing! 🔍✨**
Tools can be configured via YAML files in the `config/tools/` directory.

Example `config/tools/semgrep.yaml`:
```yaml
enabled: true
rules:
  - security
  - performance
custom_rules_path: /path/to/custom/rules
```

### Agent Configuration
Global agent settings in `config/agent.yaml`:
```yaml
parallel_execution: true
max_concurrent_tools: 4
report_formats: ['json', 'html', 'markdown']
```

## Development

### Project Structure
```
static-analysis-agent/
├── src/
│   ├── agent/
│   │   ├── core.py          # Main agent logic
│   │   ├── tool_selector.py # Tool selection algorithms
│   │   └── report_generator.py
│   ├── tools/
│   │   ├── registry.py      # Tool registry management
│   │   ├── base_tool.py     # Base tool interface
│   │   └── integrations/    # Specific tool integrations
│   └── utils/
├── config/
├── tests/
├── docs/
└── requirements.txt
```

### Adding New Tools

1. Create a new tool class inheriting from `BaseTool`
2. Implement required methods: `install()`, `run()`, `parse_output()`
3. Register the tool in `tools/registry.py`
4. Add configuration template

### Testing
```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Test with sample codebases
python scripts/test_with_sample.py
```

## Current Status

### ✅ Completed Features
- **Agent Core**: Main orchestration logic implemented
- **Tool Registry**: Dynamic tool discovery and management
- **Semgrep Integration**: First static analysis tool integrated
- **Basic Report Generation**: JSON and HTML report formats
- **Configuration System**: YAML-based configuration for agent and tools
- **CLI Interface**: Command-line interface with analyze, list-tools, install-tools commands
- **Language Detection**: Automatic detection of programming languages in codebases
- **Parallel Execution**: Concurrent tool execution framework

### 🚧 In Progress
- **Tool Expansion**: Adding more static analysis tools (Bandit, ESLint, Pylint)
- **Enhanced Reporting**: More detailed and actionable reports

### 📋 Roadmap

#### Phase 2: Tool Expansion (Next Priority)
- [ ] Add support for Bandit (Python security)
- [ ] Add support for ESLint (JavaScript/TypeScript)
- [ ] Add support for Pylint (Python code quality)
- [ ] Dependency analysis tools (Safety, OWASP Dependency-Check)
- [ ] Code quality tools (SonarQube integration)

#### Phase 3: Intelligence Enhancement
- [ ] AI-powered tool selection based on codebase characteristics
- [ ] Custom rule learning and adaptation
- [ ] Contextual recommendations and remediation suggestions
- [ ] Machine learning for false positive detection

#### Phase 4: Enterprise Features
- [ ] CI/CD integration (GitHub Actions, Jenkins, etc.)
- [ ] Web dashboard for visualization
- [ ] Historical analysis tracking and trends
- [ ] Team collaboration features
- [ ] API for integrations
