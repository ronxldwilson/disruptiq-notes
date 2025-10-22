import argparse
import os
from dotenv import load_dotenv
from src.scanner import scan_project
from src.parser import parse_file
from src.ai_model import enhance_spec_with_ai
try:
    import psutil
except ImportError:
    psutil = None

load_dotenv()

def get_active_clients():
    clients = []
    # Check Ollama first (instant check)
    if psutil and any(proc.info['name'] == 'ollama' for proc in psutil.process_iter(['name'])):
        clients.append(('ollama', 'gpt-oss:120b-cloud'))
    
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
        clients.append(('ollama', 'gpt-oss:120b-cloud'))
    
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

    # Deduplicate endpoints
    unique_endpoints = {}
    for ep in all_endpoints:
        key = (ep['path'], tuple(sorted(ep['methods'])))
        if key not in unique_endpoints:
            unique_endpoints[key] = ep
        else:
            # Merge code if different
            if ep['code'] != unique_endpoints[key]['code']:
                unique_endpoints[key]['code'] += '\n\n' + ep['code']
    all_endpoints = list(unique_endpoints.values())

    print(f"Found {len(all_endpoints)} unique endpoints.")

    print("\n--- Step 3: Enhancing the OpenAPI spec with an AI model ---")
    response_generator = enhance_spec_with_ai(all_endpoints, clients, batch_size)

    # Output is streamed to output.yaml incrementally during processing

    print("\n--- OpenAPI spec generated successfully! ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAPI Spec Agent")
    parser.add_argument("path", type=str, help="The path to the project to scan")
    args = parser.parse_args()
    clients = get_active_clients()
    print(f"Using clients in hierarchy: {[c[0] for c in clients]}")
    main(clients, args.path)
