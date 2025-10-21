import re

def parse_gin_routes(file_content):
    """Parses Go/Gin file content and extracts route information."""
    endpoints = []
    # Regex to find router.GET("/path", handler), router.POST("/path", handler), etc.
    route_pattern = re.compile(
        r"router\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\(('|")([^'"]+)('|")",
        re.IGNORECASE
    )

    for match in route_pattern.finditer(file_content):
        method = match.group(1).upper()
        path = match.group(3)
        endpoints.append({"path": path, "methods": [method]})
    return endpoints
