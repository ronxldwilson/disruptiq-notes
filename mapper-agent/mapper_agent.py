#!/usr/bin/env python3
import json
import os
import subprocess
import sys

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def run_agent(agent):
    path = agent['path']
    script = agent['script']
    name = agent['name']

    # Change to the agent directory
    cwd = os.path.abspath(path)

    try:
        # Run the script in the agent's directory
        result = subprocess.run(script, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"Error running {name}: {result.stderr}", file=sys.stderr)
            return None
        # Assume output is JSON
        output = json.loads(result.stdout.strip())
        return output
    except subprocess.TimeoutExpired:
        print(f"Timeout running {name}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON output from {name}: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running {name}: {e}", file=sys.stderr)
        return None

def main():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    unified_map = {}

    for agent in config['agents']:
        print(f"Running {agent['name']}...")
        output = run_agent(agent)
        if output is not None:
            unified_map[agent['name']] = output

    # Output the unified map
    print(json.dumps(unified_map, indent=2))

if __name__ == "__main__":
    main()
