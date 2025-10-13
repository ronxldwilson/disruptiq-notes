import re
import os

def _strip_controller_suffix(name):
    return re.sub(r'Controller$', '', name, flags=re.IGNORECASE)

def parse_aspnetcore_routes(file_path):
    """
    Very small heuristic parser for ASP.NET Core controllers.
    Returns list of {"path": "...", "methods": [...]}
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        src = f.read()

    endpoints = []

    # Find controller class and its attributes (naive: first matching ControllerBase-derived class)
    class_match = re.search(r'(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)\s*public\s+class\s+(?P<class>\w+)\s*:\s*ControllerBase', src, flags=re.IGNORECASE)
    if not class_match:
        # try to find any class if ControllerBase not present
        class_match = re.search(r'(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)\s*public\s+class\s+(?P<class>\w+)\b', src, flags=re.IGNORECASE)
    if not class_match:
        return []

    attrs_block = class_match.group('attrs') or ""
    controller_name = class_match.group('class')
    controller_segment = _strip_controller_suffix(controller_name)

    # find route attribute on controller if present
    route_attr_match = re.search(r'\[Route\(\s*"([^"]+)"\s*\)\]', attrs_block, flags=re.IGNORECASE)
    controller_route = None
    if route_attr_match:
        template = route_attr_match.group(1)
        if '[controller]' in template.lower():
            # replace [controller] with actual controller name segment
            controller_route = '/' + template.replace('[controller]', controller_segment).strip('/')
            if not controller_route.startswith('/'):
                controller_route = '/' + controller_route
        else:
            controller_route = template if template.startswith('/') else '/' + template.strip('/')
    else:
        controller_route = '/' + controller_segment

    # Find all Http* attributes and optional inline routes
    # Matches patterns like: [HttpGet], [HttpPost("route")], [HttpPut("route/{id}")]
    method_pattern = re.compile(r'\[Http(?P<verb>Get|Post|Put|Delete|Patch|Head|Options)(?:\s*\(\s*"(?P<route>[^"]*)"\s*\))?\]\s*(?:public|private|protected)?', flags=re.IGNORECASE)
    matches = method_pattern.finditer(src)

    path_map = {}  # path -> set(methods)
    for m in matches:
        verb = m.group('verb').upper()
        route = m.group('route')
        if route:
            # if route provided on method, normalize
            if route.startswith('~') or route.startswith('/'):
                # absolute route
                path = route.lstrip('~')
            else:
                # relative to controller route
                path = controller_route.rstrip('/') + '/' + route.lstrip('/')
        else:
            path = controller_route
        # normalize single slash
        if not path.startswith('/'):
            path = '/' + path
        path = re.sub(r'//+', '/', path)

        path_map.setdefault(path, set()).add(verb)

    # Convert to list of dicts
    for path, methods in path_map.items():
        endpoints.append({"path": path, "methods": sorted(methods)})

    # If no methods found, return a default GET for controller route (best-effort)
    if not endpoints:
        endpoints.append({"path": controller_route, "methods": ["GET"]})

    return endpoints
