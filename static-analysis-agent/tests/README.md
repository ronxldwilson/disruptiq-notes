# Comprehensive Test Suite

This directory contains realistic test projects designed to thoroughly test static analysis tools. Each project includes intentional issues that should be detected by various tools.

## Project Structure

### Python Projects (`python/`)

#### `flask_app/`
- **Flask web application** with realistic structure
- **Security Issues**: SQL injection, command injection, XSS, hardcoded secrets
- **Code Quality**: Unused variables, poor error handling, insecure configurations
- **Tools Tested**: bandit, pylint, flake8, semgrep

#### `django_app/`
- **Django-style application** with views and management script
- **Security Issues**: CSRF bypass, SQL injection, command injection
- **Code Quality**: Poor naming, unused functions, insecure file handling
- **Tools Tested**: bandit, pylint, flake8, semgrep

#### `data_science/`
- **Data science/ML analysis script** with pandas/numpy
- **Code Quality**: Unused imports, poor naming, memory inefficiencies
- **Security Issues**: Unsafe model serialization, hardcoded paths
- **Tools Tested**: flake8, pylint, bandit

#### `security_issues/`
- **Security-focused Python file** with intentional vulnerabilities
- **Security Issues**: Weak cryptography, SQL injection, command injection, unsafe deserialization
- **Tools Tested**: bandit (primarily), semgrep

### JavaScript Projects (`javascript/`)

#### `react_app/`
- **React application component** with modern React patterns
- **Security Issues**: XSS via dangerouslySetInnerHTML, eval usage
- **Code Quality**: Missing keys, inline functions, unused variables
- **Tools Tested**: semgrep (ESLint not installed)

#### `node_api/`
- **Express.js API server** with typical Node.js patterns
- **Security Issues**: SQL injection, command injection, path traversal
- **Code Quality**: No input validation, hardcoded credentials, poor error handling
- **Tools Tested**: semgrep

### Go Projects (`go/`)

#### `web_server/`
- **HTTP web server** with typical Go web patterns
- **Security Issues**: SQL injection, command injection, path traversal
- **Code Quality**: Poor error handling, global variables, missing validation
- **Tools Tested**: semgrep (golint not installed)

#### `cli_tool/`
- **Command-line tool** with flag parsing and file operations
- **Security Issues**: Command injection, path traversal
- **Code Quality**: Poor naming, unused functions, predictable random numbers
- **Tools Tested**: semgrep

### Mixed Projects (`mixed/`)

#### `fullstack/`
- **Multi-language fullstack application**
- **Backend**: Python Flask API with security issues
- **Frontend**: JavaScript with XSS vulnerabilities
- **Go API**: Go REST API with injection vulnerabilities
- **Tools Tested**: All tools (bandit, pylint, flake8, semgrep)

## Expected Results

When running analysis on this test suite, you should expect:

- **150+ total findings** across all tools
- **Security vulnerabilities** detected by bandit and semgrep
- **Code quality issues** detected by pylint and flake8
- **Realistic distribution** of high/medium/low severity issues

## Usage

```bash
# Run comprehensive analysis on entire test suite
python -m src analyze tests

# Run specific project analysis
python -m src analyze tests/python/flask_app

# Generate different report formats
python -m src analyze tests --output-format markdown
python -m src analyze tests --output-format summary
```

## Tool Coverage

| Tool | Python | JavaScript | Go | Security | Quality |
|------|--------|------------|---|----------|---------|
| **bandit** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **flake8** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **pylint** | ✅ | ❌ | ❌ | ⚠️ | ✅ |
| **semgrep** | ✅ | ✅ | ✅ | ✅ | ⚠️ |

## Maintenance

When adding new test cases:
1. Include realistic, production-like code
2. Add intentional issues that tools should detect
3. Document expected findings in this README
4. Test that tools actually detect the issues

This test suite ensures the static analysis agent works correctly across multiple languages and frameworks.
