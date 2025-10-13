import ast

def parse_fastapi_routes(file_content):
    """Parses FastAPI file content and extracts route information."""
    endpoints = []
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
                            path = decorator.args[0].value
                            method = decorator.func.attr.upper()
                            endpoints.append({"path": path, "methods": [method]})
    except SyntaxError:
        # Not a valid Python file, or some other parsing error
        pass
    return endpoints
