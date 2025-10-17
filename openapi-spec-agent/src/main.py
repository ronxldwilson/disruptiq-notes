import yaml
import re
import argparse
import os
from dotenv import load_dotenv
try:
    import psutil
except ImportError:
    psutil = None

load_dotenv()
from .scanner import scan_project
from .parser import parse_file
from .ai_model import enhance_spec_with_ai

def get_active_clients():
    clients = []
    # Check Ollama first (instant check)
    if psutil and any(proc.info['name'] == 'ollama' for proc in psutil.process_iter(['name'])):
        clients.append(('ollama', 'llama3.2'))
    
    # Check API keys and add clients with larger context models
    key_env = {
        'cerebras': 'CEREBRAS_API_KEY',
        'gemini': 'GEMINI_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY'
    }
    model_map = {
        'cerebras': 'llama3.3-70b',  # 128k context
        'gemini': 'gemini-2.5-flash',  # 1M context
        'openrouter': 'openai/gpt-4o'  # Large context
    }
    for client_name in ['cerebras', 'gemini', 'openrouter']:
        if os.getenv(key_env.get(client_name)):
            clients.append((client_name, model_map[client_name]))
    
    # Fallback to Ollama if nothing else
    if not clients:
        clients.append(('ollama', 'llama3.2'))
    
    return clients

def main(clients, path, batch_size=1):
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
    response_generator = enhance_spec_with_ai(all_endpoints, clients, batch_size)

    # Output is streamed to output.yaml incrementally during processing

    print("\n--- OpenAPI spec generated successfully! ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAPI Spec Agent")
    parser.add_argument("--client", type=str, help="The AI client to use (e.g., ollama, openai, claude, cerebras, gemini, openrouter). If not specified, uses hierarchy mode.")
    parser.add_argument("--model", type=str, default="llama3.2", help="The model to use for the AI client")
    parser.add_argument("--path", type=str, default="tmp", help="The path to the project to scan")
    parser.add_argument("--batch-size", type=int, default=1, help="Number of endpoints per AI batch")
    args = parser.parse_args()
    if not args.client:
        clients = get_active_clients()
        print(f"Using clients in hierarchy: {[c[0] for c in clients]}")
    else:
        clients = [(args.client, args.model)]
    main(clients, args.path, args.batch_size)
