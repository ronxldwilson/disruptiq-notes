import ast

def parse_flask_routes(file_content):
    """Parses Python file content and extracts Flask route information."""
    endpoints = []
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == 'route':
                            path = decorator.args[0].s
                            methods = [m.s for m in decorator.keywords[0].value.elts] if decorator.keywords else ['GET']
                            endpoints.append({"path": path, "methods": methods})
    except SyntaxError:
        # Not a valid Python file, or some other parsing error
        pass
    return endpoints
