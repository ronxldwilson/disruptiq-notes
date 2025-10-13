from ollama_client import get_ollama_response

def enhance_spec_with_ai(endpoints):
    """Uses an AI model to enhance the OpenAPI spec."""
    print("Sending request to AI model to enhance the OpenAPI spec...")
    prompt = (
        "Given the following API endpoints extracted from a Python Flask application, "
        "generate a complete OpenAPI 3.0.0 specification in YAML format. "
        "The specification should include:"
        "- The top-level `openapi: 3.0.0` field"
        "- A single top-level `info` section with the title, version, and description of the API."
        "- A single top-level `paths` section with a single path item for each unique path. Each path item should contain all operations (GET, POST, etc.) for that path."
        "- A single top-level `components` section with fully defined schemas for all request and response bodies."
        "- Summaries and descriptions for each endpoint."
        "- Example responses for each endpoint."
        "Do not wrap the output in a code block."
        "Endpoints:\n"
    )

    for endpoint in endpoints:
        prompt += f"- Path: {endpoint['path']}, Methods: {endpoint['methods']}\n"

    prompt += "\nPlease generate the complete OpenAPI spec based on this information."
    print(f"Prompt sent to AI model:\n{prompt}")

    # Get the AI-generated spec from Ollama
    ollama_response = get_ollama_response(prompt)
    return ollama_response
