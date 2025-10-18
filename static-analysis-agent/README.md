# Static Analysis Agent

## Overview

The Static Analysis Agent is an AI-powered tool designed to perform comprehensive static analysis on codebases. Leveraging advanced AI agents and a suite of cybersecurity and code quality tools, it autonomously analyzes code for vulnerabilities, bugs, code smells, and best practices violations. The agent makes intelligent decisions on which tools to apply based on the codebase's language, structure, and specific requirements.

## Key Features

- **Autonomous Analysis**: Uses AI agents to determine appropriate analysis tools and strategies
- **Multi-language Support**: Supports analysis for various programming languages
- **Comprehensive Tool Integration**: Integrates with industry-standard static analysis tools
- **Intelligent Reporting**: Generates detailed reports with prioritized findings
- **Customizable Rules**: Allows for custom rule sets and configurations
- **CI/CD Integration**: Can be integrated into build pipelines for automated analysis

## Architecture

### Core Components

1. **Agent Core**
   - Central decision-making engine
   - Tool selection and orchestration
   - Report generation and aggregation

2. **Tool Registry**
   - Manages available static analysis tools
   - Handles tool installation and updates
   - Provides tool configuration templates

3. **Analysis Engine**
   - Executes analysis workflows
   - Manages parallel tool execution
   - Handles tool output parsing and normalization

4. **Report Generator**
   - Aggregates findings from multiple tools
   - Prioritizes and categorizes issues
   - Generates human-readable and machine-readable reports

### Workflow

1. **Input Reception**: Receives codebase path and analysis parameters
2. **Codebase Assessment**: Analyzes codebase structure, languages, and size
3. **Tool Selection**: AI agent selects appropriate tools based on assessment
4. **Analysis Execution**: Runs selected tools in parallel where possible
5. **Result Aggregation**: Collects and normalizes outputs from all tools
6. **Report Generation**: Creates comprehensive analysis report
7. **Recommendations**: Provides actionable suggestions for code improvements

## Supported Tools

### Security Analysis
- **Semgrep**: Customizable semantic code analysis for security vulnerabilities
- **Bandit**: Security linter for Python code
- **Safety**: Checks Python dependencies for known security vulnerabilities
- **Trivy**: Comprehensive security scanner for vulnerabilities, secrets, and misconfigurations

### Code Quality
- **ESLint**: JavaScript/TypeScript linting
- **Pylint**: Python code analysis
- **SonarQube/SonarLint**: Multi-language code quality and security
- **Prettier**: Code formatting consistency checks

### Dependency Analysis
- **OWASP Dependency-Check**: Identifies vulnerable dependencies
- **Snyk**: Security and license compliance for open-source dependencies

### Other Tools
- **Cloc**: Code metrics and statistics
- **License Scanning Tools**: For open-source license compliance

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+ (for JavaScript/TypeScript analysis)
- Docker (for containerized tool execution)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd static-analysis-agent

# Install dependencies
pip install -r requirements.txt

# Install tools (the agent can handle this automatically)
python -m static_analysis_agent install-tools
```

## Usage

### Basic Analysis
```bash
python -m src analyze /path/to/codebase
```

### Advanced Options
```bash
# Specify languages to focus on
python -m src analyze /path/to/codebase --languages python,javascript

# Use specific tools
python -m src analyze /path/to/codebase --tools semgrep

# Generate HTML report
python -m src analyze /path/to/codebase --output-format html --output-file report.html
```

### List Available Tools
```bash
python -m src list-tools
```

### Install Tools
```bash
# Install all tools
python -m src install-tools

# Install specific tools
python -m src install-tools --tool semgrep --tool bandit
```

### API Usage
```python
import asyncio
from src.agent.core import StaticAnalysisAgent

async def analyze():
    agent = StaticAnalysisAgent()
    results = await agent.analyze_codebase('/path/to/codebase')
    print(f"Analysis complete: {results['success']}")

asyncio.run(analyze())
```

### Example Output
```json
{
  "success": true,
  "detected_languages": ["python"],
  "tools_used": ["semgrep"],
  "results": [...],
  "report": {
    "timestamp": "2025-10-19T00:08:06.215085",
    "languages_analyzed": ["python"],
    "tools_used": ["semgrep"],
    "summary": {
      "total_findings": 0,
      "total_errors": 0,
      "severity_breakdown": {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
      }
    }
  }
}
```

## Configuration

### Tool Configuration
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
