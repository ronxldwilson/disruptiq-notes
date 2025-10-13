import yaml
from scanner import scan_project
from parser import parse_file
from ai_model import enhance_spec_with_ai

def main():
    """The main entry point for the agent."""
    
    files = scan_project("tmp")
    all_endpoints = []
    for file in files:
        endpoints = parse_file(file)
        all_endpoints.extend(endpoints)

    openapi_spec = enhance_spec_with_ai(all_endpoints)

    with open("output.yaml", "w", encoding="utf-8") as f:
        if isinstance(openapi_spec, str):
            f.write(openapi_spec)
        else:
            yaml.dump(openapi_spec, f, sort_keys=False)

    print("OpenAPI spec generated successfully and saved to output.yaml")

if __name__ == "__main__":
    main()
