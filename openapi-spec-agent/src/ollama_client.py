import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ollama_response(prompt):
    """Sends a prompt to the Ollama API and yields the response chunks."""
    try:
        with requests.post(
            OLLAMA_API_URL,
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "stream": True
            },
            stream=True
        ) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = json.loads(chunk.decode('utf-8'))
                    yield decoded_chunk.get("response", "")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        yield None
