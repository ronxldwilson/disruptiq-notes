import os
import re
from .parsers.typescript_parser import parse_typescript_file

def extract_snippet(src, match_start):
    """Extract the entire function/method containing the match."""
    lines = src.splitlines()
    # Find the line number of the match
    char_count = 0
    match_line = 0
    for i, line in enumerate(lines):
        char_count += len(line) + 1  # +1 for newline
        if char_count > match_start:
            match_line = i
            break

    # Find function start: search backwards for 'def ', 'function ', 'func ', or decorator @
    start_line = match_line
    while start_line > 0:
        line = lines[start_line].strip()
        if re.match(r'(def|function|func)\s+\w+', line) or line.startswith('@'):
            break
        start_line -= 1

    # Find function end: search forwards for next function start or end of file
    end_line = match_line
    indent_level = len(lines[match_line]) - len(lines[match_line].lstrip())
    while end_line < len(lines) - 1:
        end_line += 1
        line = lines[end_line]
        stripped = line.strip()
        if stripped and not line.startswith(' ') * indent_level:  # Assuming consistent indentation
            if re.match(r'(def|function|func)\s+\w+', stripped) or stripped.startswith('@'):
                end_line -= 1  # Don't include next function
                break

    # Extract from start_line to end_line
    snippet = '\n'.join(lines[start_line:end_line + 1])
    return snippet

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
            endpoints.append({"path": path, "methods": [verb], "code": extract_snippet(src, m2.start())})
    return endpoints or [{"path": _normalize_path(controller_route), "methods": ["GET"], "code": ""}]

def _parse_go(src):
    endpoints = []
    # handle route groups
    group_matches = re.finditer(r'(\w+)\.Group\("([^"]+)"\)', src)
    for group_match in group_matches:
        group_var = group_match.group(1)
        group_prefix = group_match.group(2)
        # find routes within the group
        for m in re.finditer(r'' + group_var + r'\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\(\s*"([^"]+)"', src):
            verb = m.group(1).upper()
            path = _normalize_path(group_prefix + m.group(2))
            path = re.sub(r':(\w+)', r'{\1}', path) # convert gin path params to openapi format
            existing = next((e for e in endpoints if e["path"] == path), None)
            if existing:
                if verb not in existing["methods"]:
                    existing["methods"].append(verb)
            else:
                endpoints.append({"path": path, "methods": [verb], "code": extract_snippet(src, m.start())})

    # handle routes outside of groups
    for m in re.finditer(r'\b\w+\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\(\s*"([^"]+)"', src):
        verb = m.group(1).upper()
        path = _normalize_path(m.group(2))
        path = re.sub(r':(\w+)', r'{\1}', path) # convert gin path params to openapi format
        # check if the path is already handled by a group
        in_group = False
        for endpoint in endpoints:
            if endpoint["path"].startswith(path):
                in_group = True
                break
        if not in_group:
            existing = next((e for e in endpoints if e["path"] == path), None)
            if existing:
                if verb not in existing["methods"]:
                    existing["methods"].append(verb)
            else:
                endpoints.append({"path": path, "methods": [verb], "code": extract_snippet(src, m.start())})
    return endpoints

def _parse_java(src):
    # try Spring @GetMapping
    endpoints = []
    for m in re.finditer(r'@GetMapping\(\s*"([^"]+)"\s*\)', src):
        endpoints.append({"path": _normalize_path(m.group(1)), "methods": ["GET"], "code": extract_snippet(src, m.start())})
    if endpoints:
        return endpoints
    # try JAX-RS: class @Path and method @GET/@POST
    class_path = re.search(r'@Path\(\s*"([^"]+)"\s*\)', src)
    if class_path:
        base = class_path.group(1)
        for m in re.finditer(r'@(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b', src):
            verb = m.group(0).strip('@').upper()
            endpoints.append({"path": _normalize_path(base), "methods": [verb], "code": extract_snippet(src, m.start())})
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
            endpoints.append({"path": path, "methods": [verb], "code": extract_snippet(src, m.start())})
    if endpoints:
        return endpoints
    # Next.js API route heuristic: export default handler -> root path
    if re.search(r'export\s+default\s+function\s+\w*\(\s*req\s*,\s*res', src):
        return [{"path": "/", "methods": ["GET"], "code": ""}]
    return []

def _parse_python(src, ext):
    # Django: path('articles/', ...)
    if "from django.urls" in src or "urlpatterns" in src:
        endpoints = []
        for m in re.finditer(r'path\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*views\.([^,)]+)', src):
            path = m.group(1)
            view_name = m.group(2)
            methods = []
            # function-based view with @api_view
            view_func_match = re.search(r'@api_view\(\s*\[([^\]]+)\]\s*\)\s*def\s+' + view_name, src)
            if view_func_match:
                methods = [meth.strip().strip('\'"') for meth in view_func_match.group(1).split(',')]
            else:
                # class-based view
                view_class_match = re.search(r'class\s+' + view_name + r'\(APIView\):', src)
                if view_class_match:
                    class_src = src[view_class_match.end():]
                    # find end of class
                    end_of_class = re.search(r'^\w', class_src, re.MULTILINE)
                    if end_of_class:
                        class_src = class_src[:end_of_class.start()]
                    if "def get" in class_src:
                        methods.append("GET")
                    if "def post" in class_src:
                        methods.append("POST")
                    if "def put" in class_src:
                        methods.append("PUT")
                    if "def delete" in class_src:
                        methods.append("DELETE")
                    if "def patch" in class_src:
                        methods.append("PATCH")

            if not methods:
                methods = ["GET"] # default to GET
            endpoints.append({"path": path, "methods": methods, "code": extract_snippet(src, m.start())})
        return endpoints
    # FastAPI: @app.get("/items/")
    if "FastAPI" in src or "@app.get" in src:
        endpoints = []
        for m in re.finditer(r'@app\.(get|post|put|delete|patch|head|options)\(\s*["\']([^"\']+)["\']\)', src, flags=re.IGNORECASE):
            path = _normalize_path(m.group(2))
            methods = [m.group(1).upper()]
            # very basic heuristics to get request/response models
            func_line = src[m.end():].split('\n')[0]
            response_model = re.search(r'response_model=(\w+)', func_line)
            if response_model:
                response_model = response_model.group(1)
            else:
                response_model = None
            request_body = re.search(r'(\w+):\s*(\w+)', func_line)
            if request_body:
                request_body = request_body.group(2)
            else:
                request_body = None

            endpoints.append({
            "path": path,
            "methods": methods,
            "request_body": request_body,
            "response_model": response_model,
            "code": extract_snippet(src, m.start()),
            })
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
            endpoints.append({"path": _normalize_path(path), "methods": methods, "code": extract_snippet(src, m.start())})
        return endpoints
    return []

def _parse_ruby(src):
    endpoints = []
    # explicit get 'welcome/index'
    for m in re.finditer(r'\b(get|post|put|patch|delete)\s+[\'"]([^\'"]+)[\'"]', src):
        verb = m.group(1).upper()
        path = _normalize_path("/" + m.group(2).lstrip('/'))
        path = re.sub(r':(\w+)', r'{\1}', path) # convert rails path params to openapi format
        existing = next((e for e in endpoints if e["path"] == path), None)
        if existing:
            if verb not in existing["methods"]:
                existing["methods"].append(verb)
        else:
            endpoints.append({"path": path, "methods": [verb], "code": extract_snippet(src, m.start())})

    # resources :articles -> expand common RESTful routes in expected order
    for m in re.finditer(r'\bresources\s+:(\w+)', src):
        resource = m.group(1)
        endpoints.extend([
        {"path": f"/{resource}", "methods": ["GET"], "code": ""},
        {"path": f"/{resource}", "methods": ["POST"], "code": ""},
        {"path": f"/{resource}/{{id}}", "methods": ["GET"], "code": ""},
        {"path": f"/{resource}/{{id}}", "methods": ["PUT", "PATCH"], "code": ""},
        {"path": f"/{resource}/{{id}}", "methods": ["DELETE"], "code": ""},
        ])

    # nested resources
    for m in re.finditer(r'resources\s+:(\w+)\s+do\s+(.*?)\s+end', src, re.DOTALL):
        parent_resource = m.group(1)
        nested_block = m.group(2)
        for nested_m in re.finditer(r'resources\s+:(\w+)', nested_block):
            nested_resource = nested_m.group(1)
            endpoints.extend([
            {"path": f"/{parent_resource}/{{{parent_resource}_id}}/{nested_resource}", "methods": ["GET"], "code": ""},
            {"path": f"/{parent_resource}/{{{parent_resource}_id}}/{nested_resource}", "methods": ["POST"], "code": ""},
            {"path": f"/{parent_resource}/{{{parent_resource}_id}}/{nested_resource}/{{id}}", "methods": ["GET"], "code": ""},
            {"path": f"/{parent_resource}/{{{parent_resource}_id}}/{nested_resource}/{{id}}", "methods": ["PUT", "PATCH"], "code": ""},
            {"path": f"/{parent_resource}/{{{parent_resource}_id}}/{nested_resource}/{{id}}", "methods": ["DELETE"], "code": ""},
            ])

    return endpoints

def _parse_php(src):
    endpoints = []
    # Laravel routes: Route::get('/path', ...)
    for m in re.finditer(r'Route::(get|post|put|patch|delete|options|head|any)\(\s*[\'\"]([^\']+[\'\"]\s*,)', src, flags=re.IGNORECASE):
        verb = m.group(1).upper()
        if verb == 'ANY':
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        else:
            methods = [verb]
        path = _normalize_path(m.group(2))
        # Laravel uses {id}, already in OpenAPI format
        existing = next((e for e in endpoints if e["path"] == path), None)
        if existing:
            existing["methods"] = sorted(set(existing["methods"] + methods))
        else:
            endpoints.append({"path": path, "methods": methods, "code": extract_snippet(src, m.start())})
    # Symfony: @Route("/path", methods={"GET"})
    for m in re.finditer(r'@Route\(\s*[\'\"]([^\']+[\'\"]\s*)(?:,\s*methods\s*=\s*\{([^}]+)\})?', src):
        path = _normalize_path(m.group(1))
        methods_str = m.group(2)
        if methods_str:
            methods = [meth.strip().strip('\"').upper() for meth in methods_str.split(',')]
        else:
            methods = ['GET']  # default
            existing = next((e for e in endpoints if e["path"] == path), None)
            if existing:
                existing["methods"] = sorted(set(existing["methods"] + methods))
            else:
                endpoints.append({"path": path, "methods": methods, "code": extract_snippet(src, m.start())})
    return endpoints

def _parse_nestjs(src):
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
            return [{"path": base, "methods": sorted(set(methods)), "code": extract_snippet(src, ctrl.start())}]
        else:
            return [{"path": base, "methods": ["GET"], "code": extract_snippet(src, ctrl.start())}]
    return []

def parse_file(file_path):
    if not os.path.exists(file_path):
        return []

    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".ts", ".tsx"):
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        if "@nestjs/common" in src:
            return _parse_nestjs(src)
        else:
            return parse_typescript_file(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
    except Exception:
        return []

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
    if ext == ".php":
        return _parse_php(src)

    return []
