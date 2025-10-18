# Docker MCP Toolkit + Semgrep MCP Setup with Ollama GPT-OSS-120B

This setup demonstrates how Ollama, using the GPT-OSS-120B cloud model, acts as an intelligent agent that orchestrates between the Docker MCP Toolkit and Semgrep MCP to find and analyze issues in codebases.

## Understanding the Components

### Docker MCP Toolkit
The Docker MCP Toolkit (from https://hub.docker.com/mcp/) is a collection of pre-containerized MCP servers that enable LLMs to interact with various tools and services through Docker containers. It specifically allows running temporary Docker containers that provide access to underlying third-party tools via the Model Context Protocol.

Key features:
- Pre-built containerized MCP servers for popular tools
- Easy deployment with `docker run`
- Enables sandboxed execution of third-party tools
- Supports temporary container lifecycles for tool interactions

### Semgrep MCP
Your existing Semgrep MCP setup provides static code analysis capabilities for detecting vulnerabilities, security issues, and code quality problems.

### Ollama with GPT-OSS-120B Cloud
Ollama serves as the interface for the GPT-OSS-120B cloud model, configured to use MCP for tool calling and orchestration.

## Setup Instructions

### 1. Prerequisites
- Docker installed and running
- Python 3.8+ with required packages (`pip install openai`)
- Access to GPT-OSS-120B cloud API (OpenAI-compatible endpoint)
- Semgrep installed locally

### 2. Start Docker MCP Toolkit Containers

Run the container startup script:

```bash
chmod +x start_containers.sh
./start_containers.sh
```

This will start the necessary Docker MCP containers:
- Docker MCP Toolkit (for running temporary containers)
- GitHub MCP (for repository operations)
- Stripe MCP (example business tool)
- MongoDB MCP (example database tool)

### 3. Configure Environment Variables

Set your GPT-OSS-120B cloud API credentials:

```bash
export GPT_OSS_120B_API_KEY="your-actual-api-key"
export GPT_OSS_120B_BASE_URL="https://your-gpt-oss-120b-endpoint/v1"
```

### 4. Ensure Semgrep is Available

Your Semgrep MCP setup should be running. The agent will call `semgrep` commands directly.

## Running the Agent

Start the Python-based agent:

```bash
python agent.py
```

The agent will:
1. Connect to the GPT-OSS-120B cloud model
2. Provide interactive chat interface
3. Execute tools via Docker containers and Semgrep commands
4. Analyze and report on code issues

### Example Usage

```
You: Analyze the codebase in /path/to/project for security issues

Agent: I'll use Semgrep to scan for vulnerabilities and Docker tools for deeper analysis...

[Agent calls tools and analyzes results]

Agent: Found several security issues including SQL injection vulnerabilities and unsafe eval() usage...
```

## Stopping the Setup

To stop the containers:

```bash
docker stop docker-mcp-toolkit github-mcp stripe-mcp mongodb-mcp
docker rm docker-mcp-toolkit github-mcp stripe-mcp mongodb-mcp
```

## Agent Workflow for Finding Issues

The intelligent agent can now perform comprehensive issue analysis:

1. **Code Analysis**: Use Semgrep MCP to scan repositories for vulnerabilities, security issues, and code quality problems

2. **Dynamic Testing**: Leverage Docker MCP Toolkit to run temporary containers with specialized testing tools (e.g., security scanners, linters, fuzzers)

3. **Context Gathering**: Use containerized MCP servers (GitHub, monitoring tools, databases) to gather additional context about issues

4. **Orchestrated Investigation**: Combine insights from multiple sources to provide comprehensive issue reports and remediation suggestions

## Example Agent Interactions

```
User: "Analyze this codebase for security issues"

Agent (via GPT-OSS-120B):
1. Calls Semgrep MCP → Scans code for known vulnerabilities
2. Calls Docker MCP Toolkit → Runs containerized security tools for deeper analysis
3. Calls GitHub MCP → Checks for related issues/PRs
4. Synthesizes findings into actionable recommendations
```

## Key Benefits

- **Sandboxing**: Docker MCP Toolkit ensures safe execution of third-party tools
- **Scalability**: Easy to spin up/down containerized tools as needed
- **Integration**: Seamless orchestration between code analysis and dynamic testing
- **Extensibility**: Access to entire ecosystem of containerized MCP servers
- **Intelligence**: GPT-OSS-120B cloud model provides advanced reasoning over tool outputs

## Security Considerations

- Run MCP containers with appropriate resource limits
- Use secure API keys and environment variables
- Implement proper network isolation for sensitive operations
- Regularly update container images for security patches
