import requests
import json
import os
from .base_client import BaseAIClient

class OpenAIClient(BaseAIClient):
    """AI client for OpenAI."""
    def __init__(self, model, api_url="https://api.openai.com/v1/completions"):
        super().__init__(api_url, model)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

    def get_response(self, prompt):
        """Sends a prompt to the OpenAI API and yields the response chunks."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        try:
            with requests.post(self.api_url, headers=headers, json=data, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_lines():
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8')
                        if decoded_chunk.startswith('data: '):
                            json_chunk = json.loads(decoded_chunk[6:])
                            yield json_chunk['choices'][0]['text']
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to OpenAI: {e}")
            yield None