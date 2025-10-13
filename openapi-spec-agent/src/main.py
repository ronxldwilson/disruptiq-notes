import yaml
from scanner import scan_project
from parser import parse_file
from ai_model import enhance_spec_with_ai

def main():
    """The main entry point for the agent."""
    print("--- Starting OpenAPI Spec Agent ---")
    from scanner import scan_project
    from parser import parse_file
    from ai_model import enhance_spec_with_ai, generate_path_spec
    import re
    import yaml

    print("\n--- Step 1: Scanning project files ---")
    files = scan_project("tmp")
    print(f"Found {len(files)} files to parse.")

    print("\n--- Step 2: Parsing files and extracting endpoints ---")
    all_endpoints = []
    for file in files:
        endpoints = parse_file(file)
        all_endpoints.extend(endpoints)
    print(f"Found {len(all_endpoints)} endpoints.")

    print("\n--- Step 3: Enhancing the OpenAPI spec with an AI model ---")
    info_and_components_generator = enhance_spec_with_ai(all_endpoints)
    info_and_components = "".join(info_and_components_generator)

    paths = {}
    for endpoint in all_endpoints:
        path_spec_generator = generate_path_spec(endpoint)
        path_spec = "".join(path_spec_generator)
        # Remove code blocks from the AI model's output
        path_spec = re.sub(r"```(?:yml)?\n?", "", path_spec)
        paths.update(yaml.safe_load(path_spec))

    # Combine the info, components, and paths into a single spec
    spec = yaml.safe_load(info_and_components)
    spec["paths"] = paths

    print("\n--- Step 4: Saving the OpenAPI spec to output.yaml ---")
    with open("output.yaml", "w", encoding="utf-8") as f:
        yaml.dump(spec, f, sort_keys=False)

    print("\n--- OpenAPI spec generated successfully! ---")

if __name__ == "__main__":
    main()
