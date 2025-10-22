#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import threading
import time

processes = set()
processes_lock = threading.Lock()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def run_agent(agent, param=None, stop_event=None):
    if stop_event is None:
        stop_event = threading.Event()
    path = agent['path']
    script = agent['script']
    name = agent['name']

    # Build the script command
    script_cmd = script
    if param:
        script_cmd += f" {param}"

    # Change to the agent directory
    cwd = os.path.abspath(path)
    # print(f"Running {name} in directory: {cwd}")
    # print(f"Command: {script_cmd}")

    if not os.path.isdir(cwd):
        print(f"Error: Directory {cwd} does not exist for {name}", file=sys.stderr)
        return None

    try:
        # Run the script in the agent's directory
        process = subprocess.Popen(script_cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with processes_lock:
            processes.add(process)

        start_time = time.time()
        while True:
            if stop_event.is_set():
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                with processes_lock:
                    processes.discard(process)
                print(f"{name} terminated due to interrupt", file=sys.stderr)
                return None

            retcode = process.poll()
            if retcode is not None:
                break

            if time.time() - start_time > 120:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                with processes_lock:
                    processes.discard(process)
                print(f"Timeout running {name}", file=sys.stderr)
                return None

            time.sleep(0.1)

        with processes_lock:
            processes.discard(process)

        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error running {name}: Return code {process.returncode}", file=sys.stderr)
            print(f"Stderr: {stderr}", file=sys.stderr)
            print(f"Stdout: {stdout}", file=sys.stderr)
            return None

        output_str = stdout.strip()
        print(f"{name} completed successfully.")
        try:
            # Try to parse as JSON
            output = json.loads(output_str)
        except json.JSONDecodeError:
            # If not JSON, wrap the output as a list of lines
            output = {"output": output_str.splitlines() if output_str else []}
        return output
    except Exception as e:
        with processes_lock:
            if 'process' in locals() and process in processes:
                processes.discard(process)
        print(f"Error running {name}: {e}", file=sys.stderr)
        return None

def main():
    stop_event = threading.Event()
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

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = {}
            for agent in config['agents']:
                print(f"Running {agent['name']}...")
                futures[agent['name']] = executor.submit(run_agent, agent, param, stop_event)

            for agent in config['agents']:
                name = agent['name']
                output = futures[name].result()
                if output is not None:
                    unified_map[name] = output

        # Save the unified map to output.json
        with open('output.json', 'w') as f:
            json.dump(unified_map, f, indent=2)
        print("Report saved to output.json")

    except KeyboardInterrupt:
        print("Interrupted by user. Terminating all processes...", file=sys.stderr)
        stop_event.set()
        with processes_lock:
            for p in list(processes):
                try:
                    p.terminate()
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        # Wait a bit for processes to terminate
        time.sleep(1)
        sys.exit(1)

if __name__ == "__main__":
    main()
