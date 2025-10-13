from ollama_client import get_ollama_response

def generate_path_spec(endpoint):
    """Generates a YAML string for a single path."""
    print(f"Generating spec for endpoint: {endpoint['path']} ({endpoint['methods']})")
    prompt = (
        f"Given the following API endpoint: Path: {endpoint['path']}, Methods: {endpoint['methods']}, "
        "generate a complete OpenAPI 3.0.0 path item in YAML format. "
        "The path item should include methods, summaries, descriptions, and example responses for the endpoint."
        "Do not wrap the output in a code block."
    )

    # Get the AI-generated spec from Ollama
    ollama_response = get_ollama_response(prompt)
    return ollama_response

def enhance_spec_with_ai(endpoints):
    """Generates the info and components sections of the OpenAPI spec."""
    print("Generating info and components sections of the OpenAPI spec...")
    prompt = (
        "Given the following API endpoints, generate the info and components sections of an OpenAPI 3.0.0 specification in YAML format."
        "The info section should include the title, version, and description of the API."
        "The components section should include fully defined schemas for all request and response bodies."
        "Do not wrap the output in a code block."
        "Endpoints:\n"
    )

    for endpoint in endpoints:
        prompt += f"- Path: {endpoint['path']}, Methods: {endpoint['methods']}\n"

    prompt += "\nPlease generate the info and components sections of the OpenAPI spec based on this information."

    # Get the AI-generated spec from Ollama
    ollama_response = get_ollama_response(prompt)
    return ollama_response
