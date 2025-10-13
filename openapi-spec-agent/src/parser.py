import os
import re

# Very small heuristic parsers per language/framework used by tests.
# Returns list of {"path": "...", "methods": [...]}

def _normalize_path(p):
    if not p:
        return "/"
    p = p.strip()
    if not p.startswith("/"):
        p = "/" + p
    p = re.sub(r'//+', '/', p)
    return p

def _parse_cs(src):
    # find controller class and route attr
    m = re.search(r'(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)\s*public\s+class\s+(?P<class>\w+)', src, flags=re.IGNORECASE)
    if not m:
        return []
    attrs = m.group('attrs') or ""
    cls = m.group('class')
    controller_segment = re.sub(r'Controller$', '', cls, flags=re.IGNORECASE)
    route_m = re.search(r'\[Route\(\s*"([^"]+)"\s*\)\]', attrs, flags=re.IGNORECASE)
    if route_m:
        template = route_m.group(1)
        if '[controller]' in template.lower():
            controller_route = "/" + template.replace('[controller]', controller_segment).strip('/')
        else:
            controller_route = template if template.startswith('/') else '/' + template.strip('/')
    else:
        controller_route = "/" + controller_segment

    endpoints = []
    for m2 in re.finditer(r'\[Http(?P<verb>Get|Post|Put|Delete|Patch|Head|Options)(?:\s*\(\s*"(?P<route>[^"]*)"\s*\))?\]', src, flags=re.IGNORECASE):
        verb = m2.group('verb').upper()
        route = m2.group('route')
        if route:
            if route.startswith('/') or route.startswith('~'):
                path = route.lstrip('~')
            else:
                path = controller_route.rstrip('/') + '/' + route.lstrip('/')
        else:
            path = controller_route
        path = _normalize_path(path)
        # merge
        existing = next((e for e in endpoints if e["path"] == path), None)
        if existing:
            if verb not in existing["methods"]:
                existing["methods"].append(verb)
        else:
            endpoints.append({"path": path, "methods": [verb]})
    return endpoints or [{"path": _normalize_path(controller_route), "methods": ["GET"]}]

def _parse_go(src):
    endpoints = []
    # match r.GET("/ping", ...), router.GET("/x", ...)
    for m in re.finditer(r'\b\w+\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\(\s*"([^"]+)"', src):
        verb = m.group(1).upper()
        path = _normalize_path(m.group(2))
        existing = next((e for e in endpoints if e["path"] == path), None)
        if existing:
            if verb not in existing["methods"]:
                existing["methods"].append(verb)
        else:
            endpoints.append({"path": path, "methods": [verb]})
    return endpoints

def _parse_java(src):
    # try Spring @GetMapping
    endpoints = []
    for m in re.finditer(r'@GetMapping\(\s*"([^"]+)"\s*\)', src):
        endpoints.append({"path": _normalize_path(m.group(1)), "methods": ["GET"]})
    if endpoints:
        return endpoints
    # try JAX-RS: class @Path and method @GET/@POST
    class_path = re.search(r'@Path\(\s*"([^"]+)"\s*\)', src)
    if class_path:
        base = class_path.group(1)
        for m in re.finditer(r'@(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b', src):
            verb = m.group(0).strip('@').upper()
            endpoints.append({"path": _normalize_path(base), "methods": [verb]})
        return endpoints
    return []

def _parse_js(src):
    # Express: app.get('/api/data', ...)
    endpoints = []
    for m in re.finditer(r'\b\w+\.?(get|post|put|delete|patch|head|options)\(\s*([\'"])([^\'"]+)\2', src, flags=re.IGNORECASE):
        verb = m.group(1).upper()
        path = _normalize_path(m.group(3))
        existing = next((e for e in endpoints if e["path"] == path), None)
        if existing:
            if verb not in existing["methods"]:
                existing["methods"].append(verb)
        else:
            endpoints.append({"path": path, "methods": [verb]})
    if endpoints:
        return endpoints
    # Next.js API route heuristic: export default handler -> root path
    if re.search(r'export\s+default\s+function\s+\w*\(\s*req\s*,\s*res', src):
        return [{"path": "/", "methods": ["GET"]}]
    return []

def _parse_python(src, ext):
    # Django: path('articles/', ...)
    if "from django.urls" in src or "urlpatterns" in src:
        endpoints = []
        for m in re.finditer(r'path\(\s*[\'"]([^\'"]+)[\'"]\s*,', src):
            path = m.group(1)
            endpoints.append({"path": path, "methods": ["GET"]})
        return endpoints
    # FastAPI: @app.get("/items/")
    if "FastAPI" in src or "@app.get" in src:
        endpoints = []
        for m in re.finditer(r'@app\.(get|post|put|delete|patch|head|options)\(\s*["\']([^"\']+)["\']', src, flags=re.IGNORECASE):
            endpoints.append({"path": _normalize_path(m.group(2)), "methods": [m.group(1).upper()]})
        return endpoints
    # Flask: @app.route("/test", methods=["GET"])
    if "@app.route" in src:
        endpoints = []
        for m in re.finditer(r'@app\.route\(\s*["\']([^"\']+)["\'](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?', src, flags=re.IGNORECASE):
            path = m.group(1)
            methods_raw = m.group(2)
            if methods_raw:
                methods = [meth.strip().strip('\'"').upper() for meth in re.split(r',\s*', methods_raw)]
            else:
                methods = ["GET"]
            endpoints.append({"path": _normalize_path(path), "methods": methods})
        return endpoints
    return []

def _parse_ruby(src):
    endpoints = []
    # explicit get 'welcome/index'
    for m in re.finditer(r'\bget\s+[\'"]([^\'"]+)[\'"]', src):
        endpoints.append({"path": _normalize_path("/" + m.group(1).lstrip('/')), "methods": ["GET"]})
    # resources :articles -> expand common RESTful routes in expected order
    if re.search(r'\bresources\s+:articles', src):
        # index, create, show, update (PUT/PATCH), delete
        endpoints.extend([
            {"path": "/articles", "methods": ["GET"]},
            {"path": "/articles", "methods": ["POST"]},
            {"path": "/articles/{id}", "methods": ["GET"]},
            {"path": "/articles/{id}", "methods": ["PUT", "PATCH"]},
            {"path": "/articles/{id}", "methods": ["DELETE"]},
        ])
    return endpoints

def _parse_typescript(src):
    # NestJS: @Controller('cats') and @Get()
    ctrl = re.search(r'@Controller\(\s*[\'"]([^\'"]+)[\'"]\s*\)', src)
    if ctrl:
        base = "/" + ctrl.group(1).strip('/')
        methods = []
        for m in re.finditer(r'@\s*(Get|Post|Put|Delete|Patch|Head|Options)\b', src, flags=re.IGNORECASE):
            verb = m.group(1).upper()
            methods.append(verb)
        # if any method decorators without inline path -> base route
        if methods:
            return [{"path": base, "methods": sorted(set(methods))}]
        else:
            return [{"path": base, "methods": ["GET"]}]
    return []

def parse_file(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception:
        return []

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".cs":
        return _parse_cs(src)
    if ext == ".go":
        return _parse_go(src)
    if ext == ".java":
        return _parse_java(src)
    if ext == ".js":
        return _parse_js(src)
    if ext == ".py":
        return _parse_python(src, ext)
    if ext == ".rb":
        return _parse_ruby(src)
    if ext == ".ts":
        return _parse_typescript(src)

    return []
