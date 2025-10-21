import yaml
import re
import time
from .clients.base_client import get_ai_client, ContextExceeded

def enhance_spec_with_ai(endpoints, clients, batch_size=1):
    """Uses AI models to enhance the OpenAPI spec incrementally in batches, switching clients on context errors."""
    print(f"Sending requests to enhance the OpenAPI spec in batches of {batch_size} using client hierarchy...")
    current_spec_yaml = ""  # Start with empty spec
    total_batches = (len(endpoints) + batch_size - 1) // batch_size

    for i in range(0, len(endpoints), batch_size):
        batch = endpoints[i:i + batch_size]
        batch_num = i // batch_size + 1
        print(f"Processing batch {batch_num}/{total_batches}...")

        if batch_num == 1:
            # First batch: generate initial spec
            prompt = (
                "Given the following API endpoints and their corresponding code, "
                "generate a complete OpenAPI 3.0.0 specification in YAML format. "
                "**Important: The specification must be based *only* on the information provided in the code. Do not invent any new information, endpoints, or schemas.**\n\n"
                "The specification should include:\n"
                "- `openapi: 3.0.0`\n"
                "- `info`: Generate a descriptive title, version, and description for the API based on the provided endpoints.\n"
                "- `paths`: For each unique path, create a single path item and combine all HTTP methods under that path. Provide summaries, descriptions, parameters, and schemas.\n"
                "- `components`: Infer data schemas for request/response bodies from the code. Use descriptive names and include examples.\n\n"
                "Output only the YAML specification, nothing else. Do not include any explanatory text, headers, or code blocks.\n\n"
                "Here are the endpoints:\n"
            )
        else:
            # Subsequent batches: update the existing spec
            prompt = (
                f"Here is the current OpenAPI 3.0.0 specification in YAML format:\n\n{current_spec_yaml}\n\n"
                "Now, add the following new API endpoints and their corresponding code to this specification. "
                "Update the spec accordingly by adding new paths, components, and schemas based *only* on the provided code. "
                "Do not invent any new information. Merge appropriately.\n\n"
                "The updated specification should still be valid OpenAPI 3.0.0 YAML.\n\n"
                "Output only the complete updated YAML specification, nothing else. Do not include any explanatory text, headers, or code blocks.\n\n"
                "Here are the new endpoints to add:\n"
            )

        for endpoint in batch:
            prompt += f"- Path: {endpoint['path']}\n"
            prompt += f"  Methods: {endpoint['methods']}\n"
            prompt += f"  Code:\n```\n{endpoint['code']}\n```\n\n"

        if batch_num == 1:
            prompt += "Generate the OpenAPI spec for these endpoints."
        else:
            prompt += "Generate the updated OpenAPI spec with these endpoints added."

        # Save the prompt to temp.txt for auditing (overwrite each time)
        with open("temp.txt", "w", encoding="utf-8") as f:
            f.write(prompt)

        # Get the AI-generated spec, trying clients in order
        updated_spec_yaml = ""
        for client_name, model in clients:
            try:
                ai_client = get_ai_client(client_name, model)
                response_generator = ai_client.get_response(prompt)
                updated_spec_yaml = ""
                has_error = False
                for chunk in response_generator:
                    if chunk is None:
                        has_error = True
                        break
                    updated_spec_yaml += chunk
                if not has_error and updated_spec_yaml.strip():
                    break  # success
            except Exception as e:
                print(f"Error with {client_name}: {e}, trying next client...")
                continue
        else:
            print(f"Skipping batch {batch_num} due to errors with all clients.")
            continue

        # Clean and update current spec
        updated_spec_yaml = re.sub(r"```(?:yml)?\n?", "", updated_spec_yaml)
        # Extract only the YAML part starting from 'openapi:'
        match = re.search(r"(?s)openapi:\s*3\.0\.0.*", updated_spec_yaml)
        if match:
            updated_spec_yaml = match.group(0)
        else:
            print(f"Warning: Could not find valid OpenAPI YAML in response for batch {batch_num}")
        current_spec_yaml = updated_spec_yaml.strip()

        # Stream to output.yaml
        with open("output.yaml", "w", encoding="utf-8") as f:
            f.write(current_spec_yaml)
        print(f"Batch {batch_num} processed and output.yaml updated.")

        # Respect rate limits: wait 5 seconds between requests
        if batch_num < total_batches:
            print("Waiting 5 seconds to respect rate limits...")
            time.sleep(5)

    return current_spec_yaml

def merge_openapi_specs(specs):
    """Merge multiple OpenAPI specs into one."""
    if not specs:
        return {}

    # Start with the first spec
    merged = specs[0].copy()

    for spec in specs[1:]:
        # Merge info (keep the first)
        # Merge paths
        if 'paths' in spec:
            if 'paths' not in merged:
                merged['paths'] = {}
            merged['paths'].update(spec['paths'])

        # Merge components
        if 'components' in spec:
            if 'components' not in merged:
                merged['components'] = {}
            for comp_type, comp_dict in spec['components'].items():
                if comp_type not in merged['components']:
                    merged['components'][comp_type] = {}
                merged['components'][comp_type].update(comp_dict)

    return merged
