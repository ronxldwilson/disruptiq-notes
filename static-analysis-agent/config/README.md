# Configuration System

This directory contains configuration files that control the behavior of the Static Analysis Agent.

## Directory Structure

```
config/
├── README.md              # This file
├── agent.yaml            # Global agent configuration
└── tools/                # Tool-specific configurations
    ├── bandit.yaml       # Bandit (Python security) config
    ├── flake8.yaml       # Flake8 (Python style) config
    ├── pylint.yaml       # Pylint (Python quality) config
    ├── semgrep.yaml      # Semgrep (multi-language) config
    ├── eslint.yaml       # ESLint (JavaScript) config
    ├── cppcheck.yaml     # Cppcheck (C/C++) config
    ├── golint.yaml       # Golint (Go) config
    └── rubocop.yaml      # RuboCop (Ruby) config
```

## Global Configuration (agent.yaml)

Controls overall agent behavior:

### Execution Settings
- `parallel_execution`: Run tools in parallel (default: true)
- `max_concurrent_tools`: Maximum tools to run simultaneously (default: 4)
- `timeout_seconds`: Timeout for individual tool runs (default: 300)

### Output Settings
- `report_formats`: Supported output formats
- `output_dir`: Base output directory (default: 'output')
- `auto_archive`: Automatically archive old reports (default: true)

### Tool Settings
- `enabled_tools`: Tools to enable by default
- `default_languages`: Auto-detect if empty

### Logging Settings
- `verbose`: Enable verbose logging (default: false)
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Security Settings
- `fail_on_high_severity`: Fail analysis if high-severity issues found
- `minimum_severity_threshold`: Minimum severity to report

### Performance Settings
- `cache_results`: Cache tool results between runs
- `skip_unchanged_files`: Skip analysis of unmodified files

## Tool-Specific Configuration

Each tool has its own YAML configuration file that controls its behavior.

### Bandit (Python Security)
```yaml
enabled: true
severity: [high, medium, low]
confidence: [high, medium, low]
excluded_paths: ['*/test_*', '*/venv/*']
tests: []  # Specific tests to run
skips: []  # Tests to skip
baseline: null
options:
  processes: 1
  recursive: true
```

### Flake8 (Python Style)
```yaml
enabled: true
max_line_length: 88
select: [E, F, W, C, N]  # Error codes to check
ignore: [E501, W503]     # Error codes to ignore
max_complexity: 10
exclude: ['.git', '__pycache__']
filename: ['*.py']
per_file_ignores:
  __init__.py: F401
count: true
show_source: true
```

### Pylint (Python Quality)
```yaml
enabled: true
py_version: '3.8'
output_format: json
include_ids: true
ignore_patterns: ['.*\.pyc$']
disable: [C0114, C0115, C0116]
enable: [all]
confidence: [HIGH, CONTROL_FLOW]
max_line_length: 88
max_complexity: 10
```

### Semgrep (Multi-language)
```yaml
enabled: true
rules: [security, performance, correctness]
languages: []  # Auto-detect if empty
severity: [high, medium, low, info]
confidence: [high, medium, low]
exclude: ['*/test_*', '*/node_modules/*']
output_format: json
max_targets: 1000
timeout: 30
```

### ESLint (JavaScript/TypeScript)
```yaml
enabled: true
config_file: null
extensions: ['.js', '.jsx', '.ts', '.tsx']
envs: [browser, node, es6]
globals:
  console: true
rules:
  'no-console': 'off'
  'no-unused-vars': 'error'
  'eqeqeq': 'error'
plugins: []
ignore_patterns:
  - 'node_modules/'
  - '*.min.js'
max_warnings: 0
```

### Golint (Go)
```yaml
enabled: true
min_confidence: 0.8
set_exit_status: false
patterns: ['*.go']
exclude_patterns:
  - 'vendor/'
  - '*_test.go'
enable_checks: []
disable_checks: []
output_format: text
```

## Usage Examples

### Enable/Disable Tools

Edit `agent.yaml`:
```yaml
enabled_tools:
  - bandit
  - flake8
  - pylint
  # - eslint    # Uncomment to enable
```

### Customize Tool Behavior

Edit specific tool config, e.g., `tools/bandit.yaml`:
```yaml
severity: [high]  # Only report high-severity issues
excluded_paths:
  - '*/tests/*'
  - '*/migrations/*'
```

### Configure Output

Edit `agent.yaml`:
```yaml
output_dir: 'reports'
report_formats: ['json', 'html', 'markdown']
auto_archive: true
```

## Configuration Validation

The agent validates configuration files on startup and logs warnings for:
- Invalid YAML syntax
- Missing required fields
- Invalid tool names
- Incompatible settings

## Hot Reloading

Configuration changes are picked up automatically - no restart required for most settings.

## Best Practices

1. **Start with defaults**: The default configurations work well for most projects
2. **Customize gradually**: Change one setting at a time and test
3. **Use tool-specific configs**: Fine-tune individual tools rather than global overrides
4. **Version control**: Keep your config files in version control
5. **Document changes**: Comment why you made specific configuration choices

## Troubleshooting

### Tools not using config
- Check that the tool config file exists in `config/tools/`
- Verify YAML syntax is valid
- Ensure the `enabled: true` field is set

### Configuration not loading
- Check file permissions
- Verify YAML indentation
- Look for syntax errors in agent logs

### Performance issues
- Reduce `max_concurrent_tools` if system is overloaded
- Increase `timeout_seconds` for large codebases
- Use `excluded_paths` to skip irrelevant directories
