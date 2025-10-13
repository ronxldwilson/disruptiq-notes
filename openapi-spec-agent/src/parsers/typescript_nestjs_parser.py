import re

def parse_nestjs_routes(file_content):
    """Parses TypeScript/NestJS file content and extracts route information."""
    endpoints = []
    # Regex to find @Method('path') decorators
    route_pattern = re.compile(
        r"@(?:Get|Post|Put|Delete|Patch|Options|Head|All)\s*\((['\"])([^'\"]+)\1\)",
        re.IGNORECASE
    )

    for match in route_pattern.finditer(file_content):
        method = match.group(0).split('(')[0][1:].upper() # Extract method from decorator, e.g., @Get -> GET
        path = match.group(2)
        endpoints.append({"path": path, "methods": [method]})
    return endpoints
