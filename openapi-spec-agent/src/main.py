import yaml

def main():
    """The main entry point for the agent."""
    print("--- Starting OpenAPI Spec Agent ---")
    from scanner import scan_project
    from parser import parse_file
    from ai_model import enhance_spec_with_ai
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
    response_generator = enhance_spec_with_ai(all_endpoints)

    print("\n--- Step 4: Saving the OpenAPI spec to output.yaml (streaming) ---")
    with open("output.yaml", "w", encoding="utf-8") as f:
        for chunk in response_generator:
            if chunk:
                f.write(chunk)
                f.flush()

    print("\n--- OpenAPI spec generated successfully! ---")

if __name__ == "__main__":
    main()
