import re
import os

def extract_snippet(src, match_start):
    """Extract the entire function/method containing the match."""
    lines = src.splitlines()
    # Find the line number of the match
    char_count = 0
    match_line = 0
    for i, line in enumerate(lines):
        char_count += len(line) + 1  # +1 for newline
        if char_count > match_start:
            match_line = i
            break

    # Find function start: search backwards for 'function ', 'const ', or export
    start_line = match_line
    while start_line > 0:
        line = lines[start_line].strip()
        if re.match(r'(function|const|export)\s+', line) or line.startswith('@'):
            break
        start_line -= 1

    # Find function end: search forwards for next function or }
    end_line = match_line
    brace_count = 0
    while end_line < len(lines) - 1:
        end_line += 1
        line = lines[end_line]
        brace_count += line.count('{') - line.count('}')
        if brace_count == 0 and '}' in line:
            break
        if re.match(r'(function|const|export)\s+', line.strip()):
            end_line -= 1
            break

    # Extract from start_line to end_line
    snippet = '\n'.join(lines[start_line:end_line + 1])
    return snippet

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
    path = os.path.splitext(file_path)[0].replace("\\", "/")
    path = "/" + "/api/".join(path.split("/api/")[1:])
    path = path.replace("/index", "")
    path = re.sub(r'\[(.*?)\]', r'{\1}', path)

    # Find all methods in the handler
    methods = re.findall(r"if \(req.method === '([A-Z]+)'\)", code)
    if not methods:
    methods = ["GET"] # Default to GET if no methods are specified

    # Extract snippet around the handler
    handler_match = re.search(r'export\s+default', code)
    if handler_match:
    snippet = extract_snippet(code, handler_match.start())
    else:
        snippet = code  # Fallback to full code

    endpoints.append({
        "path": path,
        "methods": methods,
        "code": snippet
    })

    return endpoints
