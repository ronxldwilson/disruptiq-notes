import re
import os

def parse_nextjs_routes(file_content, file_path):
    """Parses JavaScript/TypeScript file content for Next.js API routes."""
    endpoints = []
    # Next.js API routes are typically in pages/api or app/api
    # The route is derived from the file path.
    
    # Check for the presence of a handler function, indicating an API route file
    if re.search(r"export default async function handler(req, res)", file_content) or \
       re.search(r"export default function handler(req, res)", file_content):
        
        # Extract the route from the file path
        # Example: tmp/nextjs_app/pages/api/hello.js -> /api/hello
        # Example: tmp/nextjs_app/pages/api/users/[id].js -> /api/users/{id}
        
        # Normalize path separators for consistent parsing
        normalized_path = file_path.replace(os.sep, '/')

        # Find the part of the path after 'pages/api/' or 'app/api/'
        match = re.search(r"(?:pages|app)/api/(.*)", normalized_path)
        if match:
            route_segment = match.group(1)
            # Remove file extension
            route_segment = os.path.splitext(route_segment)[0]
            
            # Handle dynamic routes: [id].js -> {id}
            route_segment = re.sub(r"[^\]]+\[([^]]+)\]", r"{\\1}", route_segment)
            
            # Construct the full API path
            api_path = "/api/" + route_segment
            
            # For simplicity, assume all methods are supported for now
            endpoints.append({"path": api_path, "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]})
            
    return endpoints
