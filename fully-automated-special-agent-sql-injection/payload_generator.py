
from cerebras import CerebrasClient
from config import CEREBRAS_API_KEY

client = CerebrasClient(api_key=CEREBRAS_API_KEY)

def query_ai(prompt):
    return client.generate(prompt=prompt).text

def generate_payloads(param_name, param_type="string"):
    prompt = f"""
    Generate context-aware SQL injection payloads for parameter `{param_name}` of type `{param_type}`.
    Return as a JSON list.
    """
    try:
        import json
        return json.loads(query_ai(prompt))
    except:
        return ["'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "' AND 'x'='y"]
