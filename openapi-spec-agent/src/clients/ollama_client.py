import requests
import json
from .base_client import BaseAIClient

class OllamaClient(BaseAIClient):
    """AI client for Ollama."""
    def __init__(self, model, api_url="http://localhost:11434/api/generate"):
        super().__init__(api_url, model)

    def get_response(self, prompt):
        """Sends a prompt to the Ollama API and yields the response chunks."""
        try:
            with requests.post(
                self.api_url,
                json={
                    "model": self.model,
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