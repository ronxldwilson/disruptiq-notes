
from concurrent.futures import ThreadPoolExecutor
from utils.http_utils import send_get, send_post
from config import BASE_URL, MAX_WORKERS

def fuzz_endpoint(endpoint, payloads):
    results = []
    method = endpoint["method"].upper()
    path = endpoint["path"]
    params = endpoint.get("params", {})

    for payload in payloads:
        injected = {k: payload if isinstance(v, str) else v for k,v in params.items()}
        if method == "GET":
            status, text = send_get(BASE_URL, path)
        else:
            status, text = send_post(BASE_URL, path, data=injected if method=="POST" else None, json_body=injected if method=="POSTJSON" else None)
        results.append({
            "payload": payload,
            "status": status,
            "text_excerpt": text[:200]
        })
    return results

def fuzz_all(endpoints):
    all_results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(fuzz_endpoint, ep, ep.get("payloads", ["'","\""])) for ep in endpoints]
        for f in futures:
            all_results.append(f.result())
    return all_results
