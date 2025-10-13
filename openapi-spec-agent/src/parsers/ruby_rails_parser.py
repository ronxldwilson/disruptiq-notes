import re

def parse_rails_routes(file_content):
    """Parses Ruby/Rails routes.rb file content and extracts route information."""
    endpoints = []
    # Regex to find get 
    # This is a simplified regex and might not cover all Rails routing complexities.
    route_pattern = re.compile(
        r"(get|post|put|patch|delete)\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE
    )

    for match in route_pattern.finditer(file_content):
        method = match.group(1).upper()  # Extract method (get, post, etc.)
        path = match.group(2)
        endpoints.append({"path": path, "methods": [method]})

    # Handle resources :name
    resources_pattern = re.compile(
        r"resources\s+:\s*([a-zA-Z_]+)"
    )
    for match in resources_pattern.finditer(file_content):
        resource_name = match.group(1)
        # For simplicity, assume standard RESTful routes for resources
        endpoints.append({"path": f"/{resource_name}", "methods": ["GET", "POST"]})
        endpoints.append({"path": f"/{resource_name}/{{id}}", "methods": ["GET", "PUT", "PATCH", "DELETE"]})

    return endpoints
