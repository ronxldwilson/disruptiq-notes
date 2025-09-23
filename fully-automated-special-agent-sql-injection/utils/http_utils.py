
import requests
from urllib.parse import urljoin

def send_get(base, path, timeout=8):
    url = urljoin(base, path)
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def send_post(base, path, data=None, json_body=None, timeout=8):
    url = urljoin(base, path)
    try:
        if json_body:
            r = requests.post(url, json=json_body, timeout=timeout)
        else:
            r = requests.post(url, data=data, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)
