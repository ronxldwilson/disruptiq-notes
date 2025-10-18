#!/usr/bin/env python3

import os
import json
import subprocess
from openai import OpenAI

# Configuration - Update these with your actual credentials
GPT_OSS_120B_API_KEY = os.getenv("GPT_OSS_120B_API_KEY", "your-api-key-here")
GPT_OSS_120B_BASE_URL = os.getenv("GPT_OSS_120B_BASE_URL", "https://api.example.com/v1")

client = OpenAI(
    api_key=GPT_OSS_120B_API_KEY,
    base_url=GPT_OSS_120B_BASE_URL
)

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_docker_container",
            "description": "Run a Docker container with specified image and command. Useful for running third-party tools in sandboxed environments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Docker image to run (e.g., 'ubuntu:latest', 'semgrep/semgrep:latest')"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to run inside the container",
                        "default": ""
                    },
                    "detach": {
                        "type": "boolean",
                        "description": "Run container in background",
                        "default": False
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the container",
                        "default": ""
                    }
                },
                "required": ["image"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_semgrep_scan",
            "description": "Run Semgrep code analysis on a specified path to find security vulnerabilities and code issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to scan (e.g., '.', '/app/src')"
                    },
                    "config": {
                        "type": "string",
                        "description": "Semgrep configuration (e.g., 'auto', 'p/security-audit')",
                        "default": "auto"
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format",
                        "default": "json",
                        "enum": ["json", "text", "sarif"]
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_github_operations",
            "description": "Perform GitHub operations using the containerized GitHub MCP server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform",
                        "enum": ["list_issues", "create_issue", "search_repos"]
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for operations that need it"
                    }
                },
                "required": ["operation"]
            }
        }
    }
]

def run_docker_container(image, command="", detach=False, name=""):
    """Run a Docker container using the Docker MCP Toolkit."""
    try:
        cmd = ["docker", "run"]
        if detach:
            cmd.append("-d")
        if name:
            cmd.extend(["--name", name])
        cmd.append("--rm")  # Remove container after execution
        cmd.append(image)
        if command:
            cmd.extend(command.split())

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            return f"Success: {result.stdout.strip()}"
        else:
            return f"Error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def run_semgrep_scan(path, config="auto", format="json"):
    """Run Semgrep scan on specified path."""
    try:
        cmd = ["semgrep", "scan", "--config", config, "--format", format, path]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for scans
        )

        if result.returncode in [0, 1]:  # Semgrep returns 1 when findings are found
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nStderr: {result.stderr.strip()}"
            return output
        else:
            return f"Error: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "Error: Semgrep scan timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def run_github_operations(operation, repo="", query=""):
    """Run GitHub operations using containerized MCP server."""
    # This is a placeholder - in real implementation, would connect to the GitHub MCP container
    # For now, return a mock response
    return f"GitHub {operation} operation would be performed on {repo or 'specified repo'} with query: {query}"

def execute_tool(tool_name, arguments):
    """Execute the appropriate tool based on name and arguments."""
    if tool_name == "run_docker_container":
        return run_docker_container(**arguments)
    elif tool_name == "run_semgrep_scan":
        return run_semgrep_scan(**arguments)
    elif tool_name == "run_github_operations":
        return run_github_operations(**arguments)
    else:
        return f"Unknown tool: {tool_name}"

def main():
    print("Docker MCP Toolkit + Semgrep Agent")
    print("Powered by GPT-OSS-120B cloud model")
    print("Type 'exit' to quit\n")

    # System message for the agent
    system_message = {
        "role": "system",
        "content": """You are an intelligent security analysis agent that can use Docker containers and Semgrep to find and analyze issues in codebases.

You have access to:
1. Docker MCP Toolkit - Run temporary containers with third-party tools for testing and analysis
2. Semgrep - Static code analysis for security vulnerabilities and code quality issues
3. GitHub operations - Repository and issue management

When analyzing code for issues:
- Start with Semgrep scans to identify static vulnerabilities
- Use Docker containers to run additional testing tools when needed
- Leverage GitHub integration for context about related issues or PRs
- Provide comprehensive analysis with remediation suggestions

Be thorough but efficient in your analysis."""
    }

    messages = [system_message]

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break

            messages.append({"role": "user", "content": user_input})

            # Get response from GPT-OSS-120B
            response = client.chat.completions.create(
                model="gpt-oss-120b",  # Adjust model name as needed
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7
            )

            message = response.choices[0].message
            messages.append(message)

            # Handle tool calls
            if message.tool_calls:
                print("Agent is calling tools...")
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    print(f"Executing: {tool_name} with args: {args}")

                    try:
                        result = execute_tool(tool_name, args)
                        print(f"Tool result: {result[:500]}{'...' if len(result) > 500 else ''}")

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })

                    except Exception as e:
                        error_msg = f"Tool execution failed: {str(e)}"
                        print(f"Error: {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_msg
                        })

                # Get final response after tool calls
                final_response = client.chat.completions.create(
                    model="gpt-oss-120b",
                    messages=messages,
                    temperature=0.7
                )
                assistant_response = final_response.choices[0].message.content
            else:
                assistant_response = message.content

            print(f"Agent: {assistant_response}")
            messages.append({"role": "assistant", "content": assistant_response})

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

if __name__ == "__main__":
    main()
