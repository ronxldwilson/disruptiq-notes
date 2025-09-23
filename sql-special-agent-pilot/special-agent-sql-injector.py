
#!/usr/bin/env python3
"""
sqli_fuzzer.py
Non-destructive SQLi tester for demo endpoints.
Supports:
 - GET endpoints (replace param values)
 - POST form endpoints (key=value pairs)
 - POST JSON endpoints (POSTJSON)
Usage:
  python sqli_fuzzer.py --base-url http://localhost:5000 --endpoints endpoints.txt --out results.json
"""

import argparse, requests, json, re, time, concurrent.futures
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

PAYLOADS = ["'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' AND 'x'='y"]

ERROR_PATTERNS = [
    re.compile(r"you have an error in your sql syntax", re.I),
    re.compile(r"pg::syntaxerror", re.I),
    re.compile(r"syntax error at or near", re.I),
    re.compile(r"unclosed quotation mark after the character string", re.I),
    re.compile(r"sqlite3", re.I),
    re.compile(r"sqlstate", re.I),
]

def detect_error(text):
    for p in ERROR_PATTERNS:
        if p.search(text or ""):
            return True, p.pattern
    return False, None

def parse_endpoint(line):
    line = line.strip()
    if not line: return None
    if line.startswith("GET "):
        return ("GET", line[4:].strip())
    if line.startswith("POSTJSON "):
        # format: POSTJSON /api {"key":"val"}
        try:
            _, rest = line.split(" ", 1)
            path, jsonbody = rest.strip().split(" ", 1)
            return ("POSTJSON", path.strip(), json.loads(jsonbody))
        except:
            return None
    if line.startswith("POST "):
        # format: POST /search q=alice
        try:
            _, rest = line.split(" ", 1)
            path, params = rest.strip().split(" ", 1)
            kv = {}
            for pair in params.split("&"):
                if "=" in pair:
                    k,v = pair.split("=",1)
                    kv[k]=v
            return ("POST", path.strip(), kv)
        except:
            return None
    # fallback: assume GET path
    return ("GET", line)

def send_get(base, path):
    url = urljoin(base, path)
    try:
        r = requests.get(url, timeout=8)
        return {"status": r.status_code, "text": r.text}
    except Exception as e:
        return {"error": str(e)}

def test_get(base, path):
    orig = send_get(base, path)
    base_status = orig.get("status")
    base_len = len(orig.get("text","") or "")
    results = []
    # try to inject into any numeric-looking param values
    parsed = urlparse(path)
    qs = parse_qs(parsed.query)
    for payload in PAYLOADS:
        # replace any numeric value with payload, else append param test
        new_qs = {}
        injected = False
        for k, vals in qs.items():
            v = vals[0]
            if v.isdigit():
                new_qs[k] = payload
                injected = True
            else:
                new_qs[k] = v
        if not injected:
            new_qs["test"] = payload
        new_query = urlencode(new_qs, doseq=False)
        new_path = parsed.path + "?" + new_query if new_query else parsed.path
        url = urljoin(base, new_path)
        try:
            r = requests.get(url, timeout=8)
            err, pat = detect_error(r.text)
            diff = len(r.text or "") - base_len
            suspicious = err or (r.status_code != base_status) or (abs(diff) > 40)
            results.append({
                "payload": payload,
                "url": url,
                "status": r.status_code if not hasattr(r,'status_code') else r.status_code,
                "length_diff": diff,
                "error_detected": bool(err),
                "error_pattern": pat
            })
        except Exception as e:
            results.append({"payload": payload, "url": url, "error": str(e)})
    return {"type":"GET", "path":path, "baseline": orig, "checks": results}

def test_post(base, path, params):
    url = urljoin(base, path)
    try:
        r0 = requests.post(url, data=params, timeout=8)
        base_status = r0.status_code; base_len = len(r0.text or "")
    except Exception as e:
        return {"type":"POST", "path":path, "error": f"baseline failure: {e}"}
    results=[]
    for payload in PAYLOADS:
        injected = {k:(payload if v and v.isdigit() else v) for k,v in params.items()}
        # if none numeric, inject into first param
        if not any(v.isdigit() for v in params.values()):
            first = next(iter(params.keys()))
            injected[first] = payload
        try:
            r = requests.post(url, data=injected, timeout=8)
            err, pat = detect_error(r.text)
            diff = len(r.text or "") - base_len
            results.append({
                "payload": payload,
                "status": r.status_code,
                "length_diff": diff,
                "error_detected": bool(err),
                "error_pattern": pat
            })
        except Exception as e:
            results.append({"payload": payload, "error": str(e)})
    return {"type":"POST", "path":path, "baseline_status": base_status, "checks": results}

def test_postjson(base, path, jbody):
    url = urljoin(base, path)
    try:
        r0 = requests.post(url, json=jbody, timeout=8)
        base_status = r0.status_code; base_len = len(r0.text or "")
    except Exception as e:
        return {"type":"POSTJSON", "path":path, "error": f"baseline failure: {e}"}
    results=[]
    for payload in PAYLOADS:
        injected = {}
        # inject payload into any string field
        for k,v in jbody.items():
            if isinstance(v, str):
                injected[k] = payload
            else:
                injected[k] = v
        if not any(isinstance(v,str) for v in jbody.values()):
            # if no strings, add a test field
            injected["test"] = payload
        try:
            r = requests.post(url, json=injected, timeout=8)
            err, pat = detect_error(r.text)
            diff = len(r.text or "") - base_len
            results.append({
                "payload": payload,
                "status": r.status_code,
                "length_diff": diff,
                "error_detected": bool(err),
                "error_pattern": pat
            })
        except Exception as e:
            results.append({"payload": payload, "error": str(e)})
    return {"type":"POSTJSON", "path":path, "baseline_status": base_status, "checks": results}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--endpoints", required=True)
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--max-workers", type=int, default=4)
    args = ap.parse_args()

    lines = open(args.endpoints).read().splitlines()
    parsed = []
    for L in lines:
        p = parse_endpoint(L)
        if p:
            parsed.append(p)

    out = {"base_url": args.base_url, "timestamp": time.time(), "results":[]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futures = []
        for p in parsed:
            if p[0]=="GET":
                futures.append(ex.submit(test_get, args.base_url, p[1]))
            elif p[0]=="POST":
                futures.append(ex.submit(test_post, args.base_url, p[1], p[2]))
            elif p[0]=="POSTJSON":
                futures.append(ex.submit(test_postjson, args.base_url, p[1], p[2]))
        for f in concurrent.futures.as_completed(futures):
            out["results"].append(f.result())
    with open(args.out, "w") as fw:
        json.dump(out, fw, indent=2)
    print("Results written to", args.out)

if __name__ == "__main__":
    main()
