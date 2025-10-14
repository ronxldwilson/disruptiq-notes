from clients.base_client import get_ai_client

def enhance_spec_with_ai(endpoints, client_name, model):
    """Uses an AI model to enhance the OpenAPI spec."""
    print(f"Sending request to {client_name} to enhance the OpenAPI spec...")
    prompt = (
        "Given the following API endpoints and their corresponding code, "
        "generate a complete OpenAPI 3.0.0 specification in YAML format. "
        "The specification should be as detailed as possible and should include the following sections:\n"
        "- `openapi: 3.0.0`\n"
        "- `info`: Generate a descriptive title, version, and description for the API based on the provided endpoints.\n"
        "- `paths`: For each endpoint, include all HTTP methods (GET, POST, PUT, DELETE, etc.). For each method, provide a summary, description, and any parameters (path, query, etc.) with their descriptions and schemas.\n"
        "- `components`: Infer data schemas for all request and response bodies from the provided code. Use descriptive names for the schemas based on the types in the code. Include examples for all schemas.\n\n"
        "Do not wrap the output in a code block.\n\n"
        "Here are the endpoints and their code:\n"
    )

    for endpoint in endpoints:
        prompt += f"- Path: {endpoint['path']}\n"
        prompt += f"  Methods: {endpoint['methods']}\n"
        prompt += f"  Code:\n```typescript\n{endpoint['code']}\n```\n\n"

    prompt += "Please generate the complete OpenAPI spec based on this information."
    print(f"Prompt sent to AI model:\n{prompt}")

    # Get the AI-generated spec from the selected client
    ai_client = get_ai_client(client_name, model)
    ai_response = ai_client.get_response(prompt)
    return ai_response
