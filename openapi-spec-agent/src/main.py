import yaml
import re
import argparse
from .scanner import scan_project
from .parser import parse_file
from .ai_model import enhance_spec_with_ai

def main(client_name, model, path):
    """The main entry point for the agent."""
    print("--- Starting OpenAPI Spec Agent ---")

    print("\n--- Step 1: Scanning project files ---")
    files = scan_project(path)
    print(f"Found {len(files)} files to parse.")

    print("\n--- Step 2: Parsing files and extracting endpoints ---")
    all_endpoints = []
    for file in files:
        endpoints = parse_file(file)
        all_endpoints.extend(endpoints)
    print(f"Found {len(all_endpoints)} endpoints.")

    print("\n--- Step 3: Enhancing the OpenAPI spec with an AI model ---")
    response_generator = enhance_spec_with_ai(all_endpoints, client_name, model)

    print("\n--- Step 4: Saving the OpenAPI spec to output.yaml (streaming) ---")
    with open("output.yaml", "w", encoding="utf-8") as f:
        for chunk in response_generator:
            if chunk:
                # Remove code blocks from the AI model's output
                chunk = re.sub(r"```(?:yml)?\n?", "", chunk)
                f.write(chunk)
                f.flush()

    print("\n--- OpenAPI spec generated successfully! ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAPI Spec Agent")
    parser.add_argument("--client", type=str, default="ollama", help="The AI client to use (e.g., ollama, openai, claude, cerebras, openrouter)")
    parser.add_argument("--model", type=str, default="llama3.2", help="The model to use for the AI client")
    parser.add_argument("--path", type=str, default="tmp", help="The path to the project to scan")
    args = parser.parse_args()
    main(args.client, args.model, args.path)
