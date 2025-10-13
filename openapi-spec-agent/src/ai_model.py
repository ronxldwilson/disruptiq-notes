from ollama_client import get_ollama_response
import json

def enhance_spec_with_ai(endpoints):
    """Uses an AI model to enhance the OpenAPI spec."""
    print("Sending request to AI model to enhance the OpenAPI spec...")
    prompt = (
        "Given the following API endpoints extracted from a Python Flask application, "
        "generate a complete OpenAPI 3.0.0 specification in YAML format. "
        "The specification should include:"
        "- A single path item for each unique path."
        "- Fully defined schemas for all request and response bodies."
        "- Summaries and descriptions for each endpoint."
        "- Example responses for each endpoint."
        "Do not wrap the output in a code block."
        "Endpoints:\n"
    )

    for endpoint in endpoints:
        prompt += f"- Path: {endpoint['path']}, Methods: {endpoint['methods']}\n"

    prompt += "\nPlease generate the OpenAPI spec based on this information."
    print(f"Prompt sent to AI model:\n{prompt}")

    # Get the AI-generated spec from Ollama
    ollama_response = get_ollama_response(prompt)

    if ollama_response:
        # The response from Ollama is a string, so we need to parse it.
        # We'll assume the AI model returns a YAML string.
        return ollama_response
    else:
        # If there was an error connecting to Ollama, return a basic spec.
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Error: Could not connect to Ollama",
                "version": "1.0.0",
                "description": "An error occurred while trying to connect to the Ollama AI model."
            },
            "paths": {}
        }
