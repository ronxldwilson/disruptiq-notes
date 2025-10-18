# Testing Semgrep MCP

## Test Project Created

I've created a test project in `test-project/` with a Python file `app.py` containing common vulnerabilities:

- Hardcoded password
- SQL injection vulnerability
- Use of `eval()` function

## Running Semgrep Scan

To test Semgrep on the project, run:

```bash
cd test-project
semgrep scan --config auto
```

This will run Semgrep with the default rules and detect issues like the `eval()` usage.

## MCP Integration

If Semgrep is set up as an MCP server, you can interact with it using MCP tools. For example, to read scan results, use the `read_mcp_resource` tool with the appropriate server name and URI.

Note: The exact server name and URI depend on how the MCP server is configured. Common patterns might be:
- Server: "semgrep"
- URI: something like "scan://path/to/project" or "results://scan-id"

Check the MCP server documentation for available resources.

