import re
import os

def parse_typescript_file(file_path):
    """
    A very basic parser for TypeScript files, specifically for Next.js API routes.
    Returns a list of endpoints, where each endpoint is a dictionary with path, methods, and code.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    endpoints = []

    # Extract path from file path
    path = os.path.splitext(file_path)[0].replace("\", "/")
    path = "/" + "/api/".join(path.split("/api/")[1:])
    path = path.replace("/index", "")
    path = re.sub(r'\[(.*?)\]', r'{\1}', path)

    # Find all methods in the handler
    methods = re.findall(r"if \(req.method === '([A-Z]+)'\)", code)
    if not methods:
        methods = ["GET"] # Default to GET if no methods are specified

    endpoints.append({
        "path": path,
        "methods": methods,
        "code": code
    })

    return endpoints
