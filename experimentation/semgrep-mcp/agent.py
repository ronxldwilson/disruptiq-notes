import requests
import json

MCP_SEMGREP_URL = "http://localhost:8080/semgrep"

def analyze_code_with_semgrep(code: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "callTool",
        "params": {
            "server": "semgrep",
            "tool": "analyze_code",
            "arguments": {"code": code}
        }
    }

    resp = requests.post(MCP_SEMGREP_URL, json=payload)
    resp.raise_for_status()
    return resp.json()

def format_results(result):
    findings = result.get("result", {}).get("content", [])
    out = ["🔍 Semgrep Analysis Report"]
    for item in findings:
        rule = item.get("rule_id", "unknown")
        msg = item.get("message", "")
        severity = item.get("severity", "info")
        loc = f"{item.get('path','?')}:{item.get('start_line','?')}"
        out.append(f"- [{severity.upper()}] {rule} at {loc}: {msg}")
    return "\n".join(out)

if __name__ == "__main__":
    sample_code = """
    def insecure_query(user_input):
        query = "SELECT * FROM users WHERE name = '" + user_input + "'"
        cursor.execute(query)
    """
    raw = analyze_code_with_semgrep(sample_code)
    print(format_results(raw))
