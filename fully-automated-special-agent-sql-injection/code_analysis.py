
import os, json
from cerebras import CerebrasClient
from config import CEREBRAS_API_KEY

client = CerebrasClient(api_key=CEREBRAS_API_KEY)

def query_ai(prompt):
    return client.generate(prompt=prompt).text

def analyze_codebase(path="."):
    endpoints = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith((".py", ".js")):  # Extend to frameworks
                with open(os.path.join(root,f), "r", encoding="utf-8") as file:
                    content = file.read()
                    prompt = f"""
                    Analyze this code and list HTTP endpoints with method, path, and parameters in JSON:
                    {content}
                    """
                    try:
                        result = query_ai(prompt)
                        endpoints.extend(json.loads(result))
                    except:
                        continue
    return endpoints
