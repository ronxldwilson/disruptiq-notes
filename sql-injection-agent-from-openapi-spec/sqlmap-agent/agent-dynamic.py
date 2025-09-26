
#!/usr/bin/env python3
import os
import subprocess
import yaml
import re
import json
from urllib.parse import urlencode, quote_plus
from pathlib import Path
import base64

# ---------- CONFIG ----------
OPENAPI_FILE = '../vulnerable-app/openapi.yaml'
LOGS_DIR = 'attack-logs-dynamic'
SQLMAP_PATH = r'F://disruptiq-notes//sqlmap-dev//sqlmap.py'
SQLMAP_EXTRA = ['--batch', '--level=5', '--risk=3']  # change as needed

# simple test values for parameter types
DEFAULT_TEST_VALUE = {
    'string': 'test',
    'integer': '1',
    'number': '1',
    'boolean': 'true',
    'object': {},
    'array': ['test'],
}

# optional: supply real credentials via env vars (for security schemes)
ENV_BEARER = os.getenv('API_BEARER_TOKEN')        # e.g. "eyJ..."
ENV_APIKEY = os.getenv('API_KEY')                # e.g. "abcd"
ENV_BASIC_USER = os.getenv('API_BASIC_USER')
ENV_BASIC_PASS = os.getenv('API_BASIC_PASS')
# ----------------------------

def load_openapi(path):
    path = Path(path)
    with open(path, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    return spec, path.parent

def resolve_ref(ref, spec, base_dir):
    """Resolve internal '#/...' refs and simple relative-file refs like './components.yaml#/schemas/S'"""
    if ref.startswith('#/'):
        parts = ref.lstrip('#/').split('/')
        node = spec
        for p in parts:
            if p not in node:
                return None
            node = node[p]
        return node
    # relative file ref e.g. './components.yaml#/components/schemas/User'
    if '#' in ref:
        file_part, path_part = ref.split('#', 1)
        file_path = (base_dir / file_part).resolve()
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            external = yaml.safe_load(f)
        target = '#'+path_part
        return resolve_ref(target, external, file_path.parent)
    # unsupported remote refs
    return None

def collect_parameters(path_item, operation, spec, base_dir):
    params = []
    for p in path_item.get('parameters', []):
        if '$ref' in p:
            resolved = resolve_ref(p['$ref'], spec, base_dir)
            if resolved: params.append(resolved)
        else:
            params.append(p)
    for p in operation.get('parameters', []):
        if '$ref' in p:
            resolved = resolve_ref(p['$ref'], spec, base_dir)
            if resolved: params.append(resolved)
        else:
            params.append(p)
    return params

def choose_test_value_for_schema(schema, spec, base_dir):
    """Recursive test value builder; uses example/default/enum/type; best-effort."""
    if schema is None:
        return 'test'
    if '$ref' in schema:
        resolved = resolve_ref(schema['$ref'], spec, base_dir)
        if resolved:
            return choose_test_value_for_schema(resolved, spec, base_dir)
    if 'example' in schema:
        return schema['example']
    if 'default' in schema:
        return schema['default']
    if 'enum' in schema and schema['enum']:
        return schema['enum'][0]
    t = schema.get('type')
    if t == 'object':
        obj = {}
        props = schema.get('properties', {})
        for k, prop_schema in props.items():
            obj[k] = choose_test_value_for_schema(prop_schema, spec, base_dir)
        return obj
    if t == 'array':
        items = schema.get('items', {})
        return [choose_test_value_for_schema(items, spec, base_dir)]
    # fallback to simple mapping
    return DEFAULT_TEST_VALUE.get(t, 'test')

def build_param_value(param, spec, base_dir):
    if 'schema' in param:
        return choose_test_value_for_schema(param['schema'], spec, base_dir)
    # fallback
    return DEFAULT_TEST_VALUE.get('string', 'test')

def substitute_path_params(path, params, spec, base_dir):
    def repl(match):
        name = match.group(1)
        for p in params:
            if p.get('name') == name and p.get('in') == 'path':
                v = build_param_value(p, spec, base_dir)
                return quote_plus(str(v))
        return '1'
    return re.sub(r'\{([^/}]+)\}', repl, path)

def security_headers_and_params(operation, spec):
    """Return (headers_dict, query_params_dict) for basic security schemes if present.
       Uses env vars for token values if set, else placeholder text.
    """
    headers = {}
    queries = {}
    # operation security -> list of security requirement objects
    sec = operation.get('security') or spec.get('security') or []
    if not sec:
        return headers, queries
    # components.secSchemes
    schemes = spec.get('components', {}).get('securitySchemes', {})
    for secreq in sec:
        for name, scopes in secreq.items():
            scheme = schemes.get(name, {})
            stype = scheme.get('type')
            if stype == 'http' and scheme.get('scheme') == 'bearer':
                token = ENV_BEARER or 'REPLACE_WITH_BEARER'
                headers['Authorization'] = f'Bearer {token}'
            elif stype == 'apiKey':
                loc = scheme.get('in')
                param_name = scheme.get('name')
                token = ENV_APIKEY or 'REPLACE_WITH_APIKEY'
                if loc == 'header':
                    headers[param_name] = token
                elif loc == 'query':
                    queries[param_name] = token
                elif loc == 'cookie':
                    headers['Cookie'] = f'{param_name}={token}'
            elif stype == 'http' and scheme.get('scheme') == 'basic':
                user = ENV_BASIC_USER or 'user'
                pwd = ENV_BASIC_PASS or 'pass'
                token = base64.b64encode(f'{user}:{pwd}'.encode()).decode()
                headers['Authorization'] = f'Basic {token}'
            # other schemes ignored for now
    return headers, queries

def construct_json_string_from_schema(schema, spec, base_dir):
    val = choose_test_value_for_schema(schema, spec, base_dir)
    # ensure JSON string
    try:
        return json.dumps(val)
    except Exception:
        return json.dumps({"test":"test"})

def construct_sqlmap_command(server_url, raw_path, method, path_item, operation, spec, base_dir):
    params = collect_parameters(path_item, operation, spec, base_dir)
    query_params = [p for p in params if p.get('in') == 'query']
    path_params = [p for p in params if p.get('in') == 'path']
    header_params = [p for p in params if p.get('in') == 'header']
    cookie_params = [p for p in params if p.get('in') == 'cookie']

    # build url and substitute path params
    path = substitute_path_params(raw_path, params, spec, base_dir)
    base = server_url.rstrip('/')
    url = base + path

    sqlmap_cmd = ['python', SQLMAP_PATH, '-u', f'"{url}"']

    param_focus = []  # names to pass to -p

    # security headers / query params
    sec_headers, sec_queries = security_headers_and_params(operation, spec)
    for hn, hv in sec_headers.items():
        sqlmap_cmd.extend(['-H', f'"{hn}: {hv}"'])

    # if operation has requestBody and it's JSON -> prepare payload
    data_string = None
    if method.lower() in ('get', 'delete', 'head', 'options'):
        if query_params or sec_queries:
            qs = {}
            for p in query_params:
                qs[p['name']] = build_param_value(p, spec, base_dir)
            qs.update(sec_queries)
            url_with_qs = url + ('?' if '?' not in url else '&') + urlencode(qs, doseq=True)
            sqlmap_cmd = ['python', SQLMAP_PATH, '-u', f'"{url_with_qs}"']
            param_focus = [p['name'] for p in query_params]
    else:
        # POST/PUT/PATCH: prefer requestBody JSON
        if 'requestBody' in operation:
            content = operation['requestBody'].get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                json_str = construct_json_string_from_schema(schema, spec, base_dir)
                data_string = json_str
                sqlmap_cmd.extend(['-H', '"Content-Type: application/json"', '--data', f"'{json_str}'"])
            elif 'application/x-www-form-urlencoded' in content:
                props = content['application/x-www-form-urlencoded'].get('schema', {}).get('properties', {})
                qs = {k: choose_test_value_for_schema(v, spec, base_dir) for k, v in props.items()}
                data_string = urlencode(qs, doseq=True)
                sqlmap_cmd.extend(['--data', f"'{data_string}'"])
            elif 'multipart/form-data' in content:
                # multipart handled as form key=value placeholders; sqlmap may not support files well
                props = content['multipart/form-data'].get('schema', {}).get('properties', {})
                qs = {k: choose_test_value_for_schema(v, spec, base_dir) for k, v in props.items()}
                data_string = urlencode(qs, doseq=True)
                sqlmap_cmd.extend(['--data', f"'{data_string}'"])
        # If still no body, but there are query params, send them in data (POST form)
        if data_string is None and query_params:
            qs = {p['name']: build_param_value(p, spec, base_dir) for p in query_params}
            sqlmap_cmd.extend(['--data', f"'{urlencode(qs)}'"])
            param_focus = [p['name'] for p in query_params]

    # add header params discovered in spec
    for h in header_params:
        val = build_param_value(h, spec, base_dir)
        sqlmap_cmd.extend(['-H', f'"{h["name"]}: {val}"'])

    # cookie params
    if cookie_params:
        cookie_str = '; '.join([f'{c["name"]}={build_param_value(c, spec, base_dir)}' for c in cookie_params])
        sqlmap_cmd.extend(['--cookie', f'"{cookie_str}"'])

    # add focus param list
    if param_focus:
        sqlmap_cmd.extend(['-p', ','.join(param_focus)])

    # add extra flags
    sqlmap_cmd.extend(SQLMAP_EXTRA)

    return ' '.join(sqlmap_cmd)

def safe_summary_to_filename(summary):
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', (summary or 'endpoint'))
    return safe[:200]  # prevents insanely long filenames

def execute_and_save_output(command, summary):
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    safe_name = safe_summary_to_filename(summary)
    log_file = os.path.join(LOGS_DIR, f'{safe_name}.log')
    print(f"[+] Running: {command}")
    with open(log_file, 'w', encoding='utf-8') as f:
        proc = subprocess.Popen(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
        proc.wait()

def main():
    spec, base_dir = load_openapi(OPENAPI_FILE)
    servers = spec.get('servers', [{'url': 'http://localhost:5000'}])
    server_url = servers[0].get('url', 'http://localhost:5000')

    for raw_path, path_item in spec.get('paths', {}).items():
        for method in ('get','post','put','delete','patch','head','options'):
            if method in path_item:
                operation = path_item[method]
                has_params = bool(path_item.get('parameters') or operation.get('parameters'))
                has_body = 'requestBody' in operation
                if not (has_params or has_body):
                    # still consider testing when security or examples are present? for now skip
                    continue
                command = construct_sqlmap_command(server_url, raw_path, method, path_item, operation, spec, base_dir)
                summary = operation.get('summary') or operation.get('operationId') or f"{method}_{raw_path}"
                execute_and_save_output(command, summary)

if __name__ == '__main__':
    main()
