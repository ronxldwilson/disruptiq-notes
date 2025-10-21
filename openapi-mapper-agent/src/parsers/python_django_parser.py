import ast
import re

def parse_django_routes(file_content):
    """Parses Django urls.py file content and extracts route information."""
    endpoints = []
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'path':
                if node.args and isinstance(node.args[0], ast.Constant):
                    path = node.args[0].value
                    # Django paths can have regex groups, simplify for now
                    path = re.sub(r'<[^>]+>', '{param}', path)
                    endpoints.append({"path": path, "methods": ["GET"]})
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'path':
                if node.args and isinstance(node.args[0], ast.Constant): # For `re_path` or similar
                    path = node.args[0].value
                    path = re.sub(r'<[^>]+>', '{param}', path)
                    path = re.sub(r'\(\?P<[^>]+>.*?\)', '{param}', path) # For regex paths
                    endpoints.append({"path": path, "methods": ["GET"]})
    except SyntaxError:
        # Not a valid Python file, or some other parsing error
        pass
    return endpoints
