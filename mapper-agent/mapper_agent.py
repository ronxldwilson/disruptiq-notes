#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def run_agent(agent, param=None):
    path = agent['path']
    script = agent['script']
    name = agent['name']

    # Build the script command
    script_cmd = script
    if param:
        script_cmd += f" {param}"

    # Change to the agent directory
    cwd = os.path.abspath(path)

    try:
        # Run the script in the agent's directory
        result = subprocess.run(script_cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"Error running {name}: {result.stderr}", file=sys.stderr)
            return None

        output_str = result.stdout.strip()
        try:
            # Try to parse as JSON
            output = json.loads(output_str)
        except json.JSONDecodeError:
            # If not JSON, wrap the output as a list of lines
            output = {"output": output_str.splitlines() if output_str else []}
        return output
    except subprocess.TimeoutExpired:
        print(f"Timeout running {name}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running {name}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Run mapper agents")
    parser.add_argument("param", help="Directory to pass to all agents")
    args = parser.parse_args()
    param = args.param

    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Config file {config_path} not found", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    unified_map = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {}
        for agent in config['agents']:
            print(f"Running {agent['name']}...")
            futures[agent['name']] = executor.submit(run_agent, agent, param)

        for agent in config['agents']:
            name = agent['name']
            output = futures[name].result()
            if output is not None:
                unified_map[name] = output

    # Save the unified map to report.json
    with open('report.json', 'w') as f:
        json.dump(unified_map, f, indent=2)
    print("Report saved to report.json")

if __name__ == "__main__":
    main()
