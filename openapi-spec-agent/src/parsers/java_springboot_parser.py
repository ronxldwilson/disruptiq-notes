import re

def parse_springboot_routes(file_content):
    """Parses Java/Spring Boot file content and extracts route information."""
    endpoints = []
    # Regex to find @RequestMapping, @GetMapping, @PostMapping, etc. annotations
    # This is a simplified regex and might not cover all Spring Boot routing complexities.
    route_pattern = re.compile(
        r"""@(?:RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\(value\s*=\s*("|')([^'"]+)("|')\)""",
        re.IGNORECASE
    )

    for match in route_pattern.finditer(file_content):
        method_annotation = match.group(0).split('(')[0][1:] # e.g., RequestMapping, GetMapping
        method = "GET" # Default method
        if "GetMapping" in method_annotation: method = "GET"
        elif "PostMapping" in method_annotation: method = "POST"
        elif "PutMapping" in method_annotation: method = "PUT"
        elif "DeleteMapping" in method_annotation: method = "DELETE"
        elif "PatchMapping" in method_annotation: method = "PATCH"
        elif "RequestMapping" in method_annotation: # RequestMapping can have method attribute
            # This is a simplification, RequestMapping can have multiple methods or none
            if "method=RequestMethod.GET" in match.group(0): method = "GET"
            elif "method=RequestMethod.POST" in match.group(0): method = "POST"
            # ... and so on for other methods

        path = match.group(2)
        endpoints.append({"path": path, "methods": [method]})
    return endpoints
