import os
from .parsers.python_flask_parser import parse_flask_routes
from .parsers.javascript_express_parser import parse_express_routes

def parse_file(file_path):
    """Parses a file and dispatches to the appropriate language-specific parser."""
    print(f"Parsing file: {file_path}")
    _, file_extension = os.path.splitext(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if file_extension == ".py":
        return parse_flask_routes(content)
    elif file_extension == ".js":
        return parse_express_routes(content)
    # Add more language parsers here as needed
    else:
        return [] # Return empty list for unsupported file types
