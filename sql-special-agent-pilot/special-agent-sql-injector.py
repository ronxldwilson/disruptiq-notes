#!/usr/bin/env python3
"""
sqli_fuzzer.py (improved)
Non-destructive SQLi tester for demo endpoints.

Usage:
  python sqli_fuzzer.py --base-url http://localhost:5000 --endpoints endpoints.txt --out results.json

Notes:
 - This script intentionally avoids destructive/time-based payloads.
 - If you want to enable heavier tests (time-based, sqlmap), add an approval workflow.
"""

import argparse
import requests
import json
import re
import time
import concurrent.futures
import os
import copy
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

# Curated safe payloads (non-destructive)
PAYLOADS = [
    "'", "\"",
    "' OR '1'='1", "\" OR \"1\"=\"1",
    "' OR 1=1 -- ", "\" OR 1=1 -- ",
    "' OR 'a'='a", "\" OR \"a\"=\"a",
    "' AND 'x'='y", "\" AND \"x\"=\"y",
    "'; --", "\"; --"
]

# SQL error regexes (case-insensitive)
ERROR_PATTERNS = [
    re.compile(r"you have an error in your sql syntax", re.I),
    re.compile(r"pg::syntaxerror", re.I),
    re.compile(r"syntax error at or near", re.I),
    re.compile(r"unclosed quotation mark after the character string", re.I),
    re.compile(r"sqlite3", re.I),
    re.compile(r"sqlstate", re.I),
    re.compile(r"mysql", re.I),
    re.compile(r"sqlite error", re.I),
    re.compile(r"sqlite3\.OperationalError", re.I),
]

# helpers
def normalize_base(url):
    if not url:
        raise ValueError("empty base url")
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
        parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid base url, no host found: {url}")
    if not url.endswith("/"):
        url = url.rstrip("/") + "/"
    return url

def excerpt(text, n=800):
    if text is None:
        return ""
    t = text if isinstance(text, str) else json.dumps(text)
    return (t[:n] + "...") if len(t) > n else t

def detect_error(text):
    if not text:
        return False, None
    for p in ERROR_PATTERNS:
        if p.search(text):
            return True, p.pattern
    return False, None

def try_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        return None

def json_diff(baseline_json, new_json):
    """Simple JSON diff metrics:
       - type_changed: bool
       - record_count_change: integer (new_count - baseline_count) if lists
       - keys_added/removed for dicts
    """
    out = {"type_changed": False, "record_count_change": None, "keys_added": [], "keys_removed": []}
    if baseline_json is None and new_json is None:
        return out
    if baseline_json is None or new_json is None:
        out["type_changed"] = True
        return out
    if type(baseline_json) != type(new_json):
        out["type_changed"] = True
        return out
    if isinstance(baseline_json, list) and isinstance(new_json, list):
        out["record_count_change"] = len(new_json) - len(baseline_json)
        return out
    if isinstance(baseline_json, dict) and isinstance(new_json, dict):
        base_keys = set(baseline_json.keys())
        new_keys = set(new_json.keys())
        out["keys_added"] = list(new_keys - base_keys)
        out["keys_removed"] = list(base_keys - new_keys)
        return out
    return out

def parse_endpoint(line):
    line = line.strip()
    if not line:
        return None
    if line.startswith("GET "):
        return ("GET", line[4:].strip())
    if line.startswith("POSTJSON "):
        try:
            _, rest = line.split(" ", 1)
            path, jsonbody = rest.strip().split(" ", 1)
            return ("POSTJSON", path.strip(), json.loads(jsonbody))
        except Exception:
            return None
    if line.startswith("POST "):
        try:
            _, rest = line.split(" ", 1)
            path, params = rest.strip().split(" ", 1)
            kv = {}
            for pair in params.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    kv[k] = v
            return ("POST", path.strip(), kv)
        except Exception:
            return None
    # fallback
    return ("GET", line)

def send_get(base, path, timeout=8):
    url = urljoin(base, path)
    try:
        r = requests.get(url, timeout=timeout)
        return {"status": r.status_code, "text": r.text, "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}

def analyze_check(baseline, response, payload, base_status, base_len, save_bodies_dir=None):
    # response: requests.Response or dict with error
    r_text = ""
    r_status = None
    r_url = None
    error = None
    if isinstance(response, dict) and response.get("error"):
        error = response["error"]
        r_text = ""
        r_status = None
        r_url = response.get("url")
    else:
        r_text = response.text if hasattr(response, "text") else (response.get("text") if isinstance(response, dict) else "")
        r_status = response.status_code if hasattr(response, "status_code") else (response.get("status") if isinstance(response, dict) else None)
        r_url = response.url if hasattr(response, "url") else (response.get("url") if isinstance(response, dict) else None)

    err_detected, err_pattern = detect_error(r_text)
    diff = (len(r_text or "") - base_len) if base_len is not None else None

    base_json = try_json_parse(baseline.get("text") if baseline else None)
    new_json = try_json_parse(r_text)
    jdiff = json_diff(base_json, new_json)

    # Decide high confidence:
    # - Status moved to 5xx OR
    # - SQL error regex matched OR
    # - JSON record_count_change > 0 (possible data exposure)
    high_conf = False
    if r_status and base_status and r_status != base_status and int(r_status) >= 500:
        high_conf = True
    if err_detected:
        high_conf = True
    if jdiff.get("record_count_change") is not None and jdiff.get("record_count_change") > 0:
        high_conf = True

    # optionally save full bodies for failing checks
    text_excerpt = excerpt(r_text, n=1200)
    saved_body_path = None
    if save_bodies_dir and high_conf:
        try:
            os.makedirs(save_bodies_dir, exist_ok=True)
            timestamp = int(time.time() * 1000)
            filename = f"body_{timestamp}.txt"
            saved_body_path = os.path.join(save_bodies_dir, filename)
            with open(saved_body_path, "w", encoding="utf-8") as fh:
                fh.write(f"URL: {r_url}\n\n")
                fh.write(r_text or "")
        except Exception:
            saved_body_path = None

    return {
        "payload": payload,
        "url": r_url,
        "status": r_status,
        "length_diff": diff,
        "error_detected": bool(err_detected),
        "error_pattern": err_pattern,
        "text_excerpt": text_excerpt,
        "json_diff": jdiff,
        "high_confidence": bool(high_conf),
        "saved_body": saved_body_path,
        "raw_error": error
    }

def test_get(base, path, timeout=8, save_bodies_dir=None):
    baseline = send_get(base, path, timeout=timeout)
    base_status = baseline.get("status")
    base_len = len(baseline.get("text", "") or "") if baseline.get("text") is not None else None

    parsed = urlparse(path)
    qs = parse_qs(parsed.query)
    results = []
    for payload in PAYLOADS:
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
        new_path = parsed.path + ("?" + new_query if new_query else "")
        url = urljoin(base, new_path)
        try:
            r = requests.get(url, timeout=timeout)
            results.append(analyze_check(baseline, r, payload, base_status, base_len, save_bodies_dir))
        except Exception as e:
            results.append({"payload": payload, "url": url, "error": str(e)})
    return {"type": "GET", "path": path, "baseline": baseline, "checks": results}

def test_post(base, path, params, timeout=8, save_bodies_dir=None):
    url = urljoin(base, path)
    try:
        r0 = requests.post(url, data=params, timeout=timeout)
        base_status = r0.status_code; base_len = len(r0.text or "")
        baseline = {"status": base_status, "text": r0.text, "url": url}
    except Exception as e:
        return {"type": "POST", "path": path, "error": f"baseline failure: {e}"}
    results = []
    for payload in PAYLOADS:
        injected = {k: (payload if (v and v.isdigit()) else v) for k, v in params.items()}
        if not any(v.isdigit() for v in params.values()):
            first = next(iter(params.keys()))
            injected[first] = payload
        try:
            r = requests.post(url, data=injected, timeout=timeout)
            results.append(analyze_check(baseline, r, payload, base_status, base_len, save_bodies_dir))
        except Exception as e:
            results.append({"payload": payload, "error": str(e)})
    return {"type": "POST", "path": path, "baseline_status": base_status, "checks": results}

def test_postjson(base, path, jbody, timeout=8, save_bodies_dir=None):
    url = urljoin(base, path)
    try:
        r0 = requests.post(url, json=jbody, timeout=timeout)
        base_status = r0.status_code; base_len = len(r0.text or "")
        baseline = {"status": base_status, "text": r0.text, "url": url}
    except Exception as e:
        return {"type": "POSTJSON", "path": path, "error": f"baseline failure: {e}"}
    results = []
    # For JSON we will inject into each string field individually to better localize vulnerability
    string_fields = [k for k,v in jbody.items() if isinstance(v, str)]
    if not string_fields:
        # fallback: inject into a synthetic "test" field
        string_fields = ["test"]

    for payload in PAYLOADS:
        # For each string field, create a separate injected body variant
        for field in string_fields:
            injected = copy.deepcopy(jbody)
            injected[field] = payload
            try:
                r = requests.post(url, json=injected, timeout=timeout)
                # annotate payload with the field name for clarity
                payload_label = f"{payload} (field={field})"
                results.append(analyze_check(baseline, r, payload_label, base_status, base_len, save_bodies_dir))
            except Exception as e:
                results.append({"payload": payload, "field": field, "error": str(e)})
    return {"type": "POSTJSON", "path": path, "baseline_status": base_status, "checks": results}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--endpoints", required=True)
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--max-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument("--save-bodies", type=str, default=None, help="directory to save full response bodies for high-confidence findings")
    args = ap.parse_args()

    try:
        base = normalize_base(args.base_url)
    except Exception as e:
        print("Invalid --base-url:", e)
        return

    lines = open(args.endpoints).read().splitlines()
    parsed = []
    for L in lines:
        p = parse_endpoint(L)
        if p:
            parsed.append(p)

    out = {"base_url": base, "timestamp": time.time(), "results": []}
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futures = []
        for p in parsed:
            if p[0] == "GET":
                futures.append(ex.submit(test_get, base, p[1], args.timeout, args.save_bodies))
            elif p[0] == "POST":
                futures.append(ex.submit(test_post, base, p[1], p[2], args.timeout, args.save_bodies))
            elif p[0] == "POSTJSON":
                futures.append(ex.submit(test_postjson, base, p[1], p[2], args.timeout, args.save_bodies))
        for f in concurrent.futures.as_completed(futures):
            try:
                out["results"].append(f.result())
            except Exception as e:
                out["results"].append({"error": str(e)})
    duration = time.time() - start

    # Write results
    with open(args.out, "w", encoding="utf-8") as fw:
        json.dump(out, fw, indent=2, ensure_ascii=False)

    # Summary printing
    total_checks = 0
    high_conf = []
    for r in out["results"]:
        checks = r.get("checks", [])
        total_checks += len(checks)
        for c in checks:
            if c.get("high_confidence"):
                high_conf.append({
                    "path": r.get("path"),
                    "payload": c.get("payload"),
                    "status": c.get("status"),
                    "text_excerpt": c.get("text_excerpt"),
                    "json_diff": c.get("json_diff"),
                    "saved_body": c.get("saved_body")
                })

    print(f"Run completed in {duration:.1f}s — endpoints: {len(out['results'])}, checks: {total_checks}")
    if high_conf:
        print(f"High-confidence findings: {len(high_conf)}")
        for i, h in enumerate(high_conf, 1):
            print(f"\n[{i}] {h['path']}  payload={h['payload']}  status={h['status']}")
            if h.get("json_diff"):
                print("    json_diff:", h["json_diff"])
            if h.get("saved_body"):
                print("    saved body:", h["saved_body"])
            print("    excerpt:", (h["text_excerpt"] or "").replace("\n", " ")[:200], "...")
    else:
        print("No high-confidence findings detected.")

    print("Results written to", args.out)

if __name__ == "__main__":
    main()
