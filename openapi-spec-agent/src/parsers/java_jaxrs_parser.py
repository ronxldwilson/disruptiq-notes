import re

def parse_jaxrs_routes(file_content):
    """Parses Java/JAX-RS file content and extracts route information."""
    endpoints = []
    base_path = ""

    # Find base @Path annotation for the class
    class_path_match = re.search(r'@Path\((["\'])([^"\']+)\1\)', file_content)
    if class_path_match:
        base_path = class_path_match.group(2)

    # Regex to find @Path, @GET, @POST, etc. annotations on methods
    method_route_pattern = re.compile(
        r'@(?:Path|GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s*(?:\(\s*(["\'])([^"\']+)\1\s*\))?',
        re.IGNORECASE
    )

    for match in method_route_pattern.finditer(file_content):
        method_annotation = match.group(0).split('(')[0][1:] # e.g., Path, GET
        method = "GET" # Default method if only @Path is present

        if "GET" in method_annotation: method = "GET"
        elif "POST" in method_annotation: method = "POST"
        elif "PUT" in method_annotation: method = "PUT"
        elif "DELETE" in method_annotation: method = "DELETE"
        elif "PATCH" in method_annotation: method = "PATCH"
        elif "HEAD" in method_annotation: method = "HEAD"
        elif "OPTIONS" in method_annotation: method = "OPTIONS"

        relative_path = match.group(2)
        full_path = (base_path + "/" + relative_path).replace("//", "/")
        endpoints.append({"path": full_path, "methods": [method]})
    return endpoints
