import os
import subprocess
import yaml
import re
import json
from urllib.parse import urlencode

# Constants (adjust paths)
OPENAPI_FILE = '../vulnerable-app/openapi.yaml'
LOGS_DIR = 'attack-logs'
SQLMAP_PATH = r'F://disruptiq-notes//sqlmap-dev//sqlmap.py'

# simple test values for parameter types
DEFAULT_TEST_VALUE = {
    'string': 'test',
    'integer': '1',
    'number': '1',
    'boolean': 'true',
}

def load_openapi(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def resolve_ref(ref, spec):
    """Resolve simple internal $ref like '#/components/parameters/ParamName'"""
    if not ref.startswith('#/'):
        return None
    parts = ref.lstrip('#/').split('/')
    node = spec
    for p in parts:
        if p not in node:
            return None
        node = node[p]
    return node

def collect_parameters(path_item, operation, spec):
    """Collect parameters from path-level and operation-level, resolving refs."""
    params = []
    # path-level parameters
    for p in path_item.get('parameters', []):
        if '$ref' in p:
            resolved = resolve_ref(p['$ref'], spec)
            if resolved: params.append(resolved)
        else:
            params.append(p)
    # operation-level parameters
    for p in operation.get('parameters', []):
        if '$ref' in p:
            resolved = resolve_ref(p['$ref'], spec)
            if resolved: params.append(resolved)
        else:
            params.append(p)
    return params

def build_param_value(param, spec):
    """Return a test value for parameter based on schema/type. Basic support only."""
    if 'schema' in param:
        schema = param['schema']
        if '$ref' in schema:
            resolved = resolve_ref(schema['$ref'], spec)
            if resolved and 'type' in resolved:
                return DEFAULT_TEST_VALUE.get(resolved['type'], 'test')
        if 'type' in schema:
            return DEFAULT_TEST_VALUE.get(schema['type'], 'test')
    # fallback
    return 'test'

def substitute_path_params(path, params, spec):
    """Replace {param} in path with a test value if defined in params (path-in params)."""
    def repl(match):
        name = match.group(1)
        # find parameter with that name and in=path
        for p in params:
            if p.get('name') == name and p.get('in') == 'path':
                return build_param_value(p, spec)
        # fallback
        return '1'
    return re.sub(r'\{([^/}]+)\}', repl, path)

def construct_sqlmap_command(server_url, raw_path, method, path_item, operation, spec):
    """Construct a robust sqlmap command covering query, path and request bodies."""
    params = collect_parameters(path_item, operation, spec)
    # split params by location
    query_params = [p for p in params if p.get('in') == 'query']
    path_params = [p for p in params if p.get('in') == 'path']
    header_params = [p for p in params if p.get('in') == 'header']
    cookie_params = [p for p in params if p.get('in') == 'cookie']

    # substitute path params into path
    path = substitute_path_params(raw_path, params, spec)
    url = server_url.rstrip('/') + path

    sqlmap_parts = ['python', SQLMAP_PATH, '-u', f'"{url}"']

    # Build parameter list and values
    param_names_to_specify = []
    data_string = None
    if method.lower() in ('get', 'delete'):
        # Create query string
        if query_params:
            qs = {p['name']: build_param_value(p, spec) for p in query_params}
            url_with_qs = url + ('?' if '?' not in url else '&') + urlencode(qs)
            sqlmap_parts = ['python', SQLMAP_PATH, '-u', f'"{url_with_qs}"']
            param_names_to_specify = [p['name'] for p in query_params]
    else:
        # For POST/PUT/PATCH try requestBody first (operation level)
        if 'requestBody' in operation:
            content = operation['requestBody'].get('content', {})
            # prefer JSON if present
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                # build a trivial json object from properties if possible
                payload = {}
                if 'properties' in schema:
                    for prop, prop_schema in schema['properties'].items():
                        if '$ref' in prop_schema:
                            resolved = resolve_ref(prop_schema['$ref'], spec)
                            t = resolved.get('type') if resolved else None
                        else:
                            t = prop_schema.get('type')
                        payload[prop] = DEFAULT_TEST_VALUE.get(t, 'test')
                else:
                    # fallback simple payload
                    payload = {"test": "test"}
                json_str = json.dumps(payload)
                data_string = json_str
                sqlmap_parts.extend(['-H', '"Content-Type: application/json"', '--data', f"'{json_str}'"])
            elif 'application/x-www-form-urlencoded' in content:
                props = content['application/x-www-form-urlencoded']['schema'].get('properties', {})
                qs = {k: 'test' for k in props.keys()}
                data_string = urlencode(qs)
                sqlmap_parts.extend(['--data', f"'{data_string}'"])
        # If no requestBody, but query params exist, send them in --data for POST
        if data_string is None and query_params:
            qs = {p['name']: build_param_value(p, spec) for p in query_params}
            data_string = urlencode(qs)
            sqlmap_parts.extend(['--data', f"'{data_string}'"])
            param_names_to_specify = [p['name'] for p in query_params]

    # If we have header or cookie params, add them (basic)
    for h in header_params:
        val = build_param_value(h, spec)
        sqlmap_parts.extend(['-H', f'"{h["name"]}: {val}"'])
    if cookie_params:
        cookie_str = '; '.join([f'{c["name"]}={build_param_value(c, spec)}' for c in cookie_params])
        sqlmap_parts.extend(['--cookie', f'"{cookie_str}"'])

    # Add param list (-p) so sqlmap focuses on those params
    if param_names_to_specify:
        sqlmap_parts.extend(['-p', ','.join(param_names_to_specify)])

    # Add other sqlmap options (tunable)
    sqlmap_parts.extend(['--batch', '--level=5', '--risk=3'])

    return ' '.join(sqlmap_parts)

def execute_and_save_output(command, summary):
    safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', summary or 'endpoint')
    log_file = os.path.join(LOGS_DIR, f'{safe_name}.log')
    print(f"[+] Running: {command}")
    with open(log_file, 'w', encoding='utf-8') as f:
        proc = subprocess.Popen(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
        proc.wait()

def main():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    spec = load_openapi(OPENAPI_FILE)
    server_url = spec.get('servers', [{'url': 'http://localhost:5000'}])[0]['url']

    for raw_path, path_item in spec.get('paths', {}).items():
        # path_item can contain non-method keys; handle methods explicitly
        for method in ('get','post','put','delete','patch','head','options'):
            if method in path_item:
                operation = path_item[method]
                # consider potential target if there are parameters (path or op) or requestBody
                has_params = bool(path_item.get('parameters') or operation.get('parameters'))
                has_body = 'requestBody' in operation
                if not (has_params or has_body):
                    # Skip endpoints with no declared inputs (likely not injectable)
                    continue
                command = construct_sqlmap_command(server_url, raw_path, method, path_item, operation, spec)
                summary = operation.get('summary') or operation.get('operationId') or f"{method}_{raw_path}"
                execute_and_save_output(command, summary)

if __name__ == '__main__':
    main()