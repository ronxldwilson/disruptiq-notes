import subprocess
import json
import ollama
from jsonrpcclient import parse, request_json
import shlex
import time
from pathlib import Path
import threading
import queue

# -----------------------------
# 1️⃣ MCP Gateway management (lazy start / restart from config)
# -----------------------------
gateway_proc = None
DEFAULT_GATEWAY_CMD = ["docker", "mcp", "gateway", "run"]
CONFIG_PATH = Path(__file__).parent / "mcp-ollama.json"

def load_gateway_cmd_from_config():
    """Load gateway command from mcp-ollama.json if available, fall back to default."""
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            # common keys: "gateway_cmd": [..] or "command": "docker mcp gateway run" or "run": [...]
            if isinstance(data.get("gateway_cmd"), list):
                return data["gateway_cmd"]
            if isinstance(data.get("run"), list):
                return data["run"]
            if isinstance(data.get("command"), str):
                return shlex.split(data["command"])
    except Exception as e:
        print("⚠️ Failed to read mcp-ollama.json:", e)
    return DEFAULT_GATEWAY_CMD

def start_gateway(cmd=None):
    """Start the MCP gateway subprocess and assign to global gateway_proc.

    Try list-form Popen first. If the process immediately exits or emits no output
    (which can happen with some docker wrapper commands on Windows), try a shell
    invocation fallback. If both fail, print diagnostics — the script requires
    a gateway that runs in the foreground and speaks over stdio.
    """
    global gateway_proc
    raw_cmd = cmd or load_gateway_cmd_from_config()
    # normalize: keep both forms available
    if isinstance(raw_cmd, list):
        cmd_list = raw_cmd
        cmd_str = " ".join(shlex.quote(str(x)) for x in raw_cmd)
    else:
        cmd_list = raw_cmd.split() if isinstance(raw_cmd, str) else raw_cmd
        cmd_str = raw_cmd if isinstance(raw_cmd, str) else " ".join(map(str, cmd_list))

    # ensure previous process gone
    if gateway_proc is not None and gateway_proc.poll() is None:
        try:
            gateway_proc.kill()
            gateway_proc.wait(timeout=2)
        except Exception:
            pass

    # Helper to actually spawn
    def _spawn(use_shell=False, cmd_to_use=None):
        try:
            if use_shell:
                print(f"🔁 Starting gateway (shell) with: {cmd_to_use}")
                return subprocess.Popen(
                    cmd_to_use,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            else:
                print(f"🔁 Starting gateway (list) with: {cmd_to_use}")
                return subprocess.Popen(
                    cmd_to_use,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
        except Exception as e:
            print("⚠️ Failed to spawn gateway process:", e)
            return None

    # Try list-form first (preferred)
    gateway_proc = _spawn(use_shell=False, cmd_to_use=cmd_list)
    time.sleep(1.0)

    # Quick health check: process alive and not immediately exited
    if gateway_proc is None or gateway_proc.poll() is not None:
        # Try shell fallback
        print("⚠️ Gateway process exited immediately or failed. Trying shell fallback...")
        gateway_proc = _spawn(use_shell=True, cmd_to_use=cmd_str)
        time.sleep(1.0)

    # If still not usable, print guidance
    if gateway_proc is None or gateway_proc.poll() is not None:
        print("❗ Unable to start a usable MCP gateway process from the configured command.")
        print("This script requires the gateway to run in the foreground and communicate over stdio.")
        print("Please either:")
        print("  • Ensure 'mcp-ollama.json' contains a command that runs the gateway in the foreground (no -d / --detach),")
        print("  • or start the gateway manually from a terminal with: docker mcp gateway run")
        print("After starting the gateway manually the script should be able to send JSON-RPC requests.")
    else:
        print("✅ Gateway started (pid=%s)." % gateway_proc.pid)

def _read_gateway_response(timeout=30.0):
    """Read a Content-Length framed JSON-RPC response from gateway_proc.stdout with timeout.
    Returns the raw JSON string or None on timeout/error.
    """
    if gateway_proc is None or gateway_proc.stdout is None:
        return None
    q = queue.Queue()

    def _reader():
        try:
            # read headers until empty line
            headers = {}
            while True:
                line = gateway_proc.stdout.readline()
                if not line:
                    # EOF or closed
                    q.put(None)
                    return
                line = line.strip("\r\n")
                if line == "":
                    break
                parts = line.split(":", 1)
                if len(parts) == 2:
                    headers[parts[0].strip().lower()] = parts[1].strip()
            # parse content-length
            length = headers.get("content-length")
            if length is None:
                q.put(None)
                return
            try:
                n = int(length)
            except Exception:
                q.put(None)
                return
            # read exactly n characters
            body = ""
            remaining = n
            while remaining > 0:
                chunk = gateway_proc.stdout.read(remaining)
                if chunk == "" or chunk is None:
                    q.put(None)
                    return
                body += chunk
                remaining = n - len(body)
            q.put(body)
        except Exception:
            q.put(None)

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None

def ensure_gateway_running():
    """Ensure the gateway subprocess is running; start it if not."""
    global gateway_proc
    if gateway_proc is None or gateway_proc.poll() is not None:
        start_gateway()

# -----------------------------
# 2️⃣ Chat with Ollama
# -----------------------------
def chat_with_ollama(prompt):
    """Send prompt to Ollama and get response."""
    response = ollama.chat(
        model="gpt-oss:120b-cloud",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# -----------------------------
# 3️⃣ Handle Ollama messages
# -----------------------------
def handle_agent_message(message):
    """Detect JSON tool calls and execute them."""
    try:
        data = json.loads(message)
        if "method" in data and data["method"].startswith("tools."):
            print(f"🧰 Tool call detected: {data['method']}")
            result = call_mcp(data["method"], data.get("params", {}))
            print("🔧 Tool result:", result)

            # Feed results back to Ollama for further reasoning
            followup = chat_with_ollama(
                f"Tool '{data['method']}' executed with result:\n{result}\n\n"
                "Continue reasoning or provide next instructions."
            )
            # Recursively handle next tool calls
            handle_agent_message(followup)
        else:
            # Plain text response
            print("🤖 Ollama:", message)
    except json.JSONDecodeError:
        # Non-JSON text is treated as a normal response
        print("🤖 Ollama:", message)

# -----------------------------
# 4️⃣ Main agent loop
# -----------------------------
def main():
    print("🚀 MCP-Ollama Agent started. Type a prompt.")
    system_prompt = (
        "You are an agent that must respond with JSON tool calls "
        "when instructed to run tools like Semgrep. "
        "Format:\n"
        "{\n"
        "  \"method\": \"tools.<tool_name>\",\n"
        "  \"params\": { ... }\n"
        "}\n"
        "Always respond in JSON when a tool needs to be executed."
    )

    while True:
        user_input = input("\n🗣️  You: ")
        full_prompt = f"{system_prompt}\nUser request:\n{user_input}"
        reply = chat_with_ollama(full_prompt)
        handle_agent_message(reply)

def call_mcp(method, params):
    """Send a JSON-RPC request to the MCP gateway via stdio using Content-Length framing."""
    params = params or {}
    payload = request_json(method, params=params)  # JSON string
    # Compose Content-Length framed message (no extra newline after payload)
    payload_bytes = payload.encode("utf-8")
    header = f"Content-Length: {len(payload_bytes)}\r\n\r\n"
    message = header + payload

    # Try twice: initial attempt, then restart gateway from config and retry if no response
    for attempt in range(2):
        ensure_gateway_running()
        try:
            gateway_proc.stdin.write(message)
            gateway_proc.stdin.flush()
        except Exception as e:
            print("⚠️ Failed to send request to MCP gateway (will try restart):", e)
            try:
                gateway_proc.kill()
            except Exception:
                pass
            start_gateway(load_gateway_cmd_from_config())
            continue

        # read framed response; first attempt 30s, retry 40s
        resp_body = _read_gateway_response(timeout=30.0 if attempt == 0 else 40.0)
        if not resp_body:
            if attempt == 0:
                print("⚠️ No response received from MCP gateway. Restarting gateway and retrying...")
                try:
                    gateway_proc.kill()
                except Exception:
                    pass
                start_gateway(load_gateway_cmd_from_config())
                # quick diagnostic read (give gateway slightly more time)
                try:
                    diag = _read_gateway_response(timeout=2.0)
                    if diag:
                        print("🔴 Gateway response during restart (debug):", diag.strip())
                except Exception:
                    pass
                continue
            else:
                print("❗ No response received from MCP gateway after restart attempts. Proceeding without tool result.")
                return None

        # parse JSON-RPC response string
        resp = parse(resp_body)
        return resp.result if hasattr(resp, "result") else resp.data

if __name__ == "__main__":
    main()
