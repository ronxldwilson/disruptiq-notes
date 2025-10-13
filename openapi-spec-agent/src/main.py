def main():
    """The main entry point for the agent."""
    from scanner import scan_project
    from parser import parse_file
    from generator import generate_openapi_spec

    files = scan_project("tmp")
    all_endpoints = []
    for file in files:
        endpoints = parse_file(file)
        all_endpoints.extend(endpoints)

    openapi_spec = generate_openapi_spec(all_endpoints)
    print(openapi_spec)

if __name__ == "__main__":
    main()
