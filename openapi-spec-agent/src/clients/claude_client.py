import requests
import json
import os
from .base_client import BaseAIClient

class ClaudeClient(BaseAIClient):
    """AI client for Claude (Anthropic)."""
    def __init__(self, model, api_url="https://api.anthropic.com/v1/messages"):
        super().__init__(api_url, model)
        self.api_key = os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY environment variable not set.")

    def get_response(self, prompt):
        """Sends a prompt to the Claude API and yields the response chunks."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
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
                            if json_chunk['type'] == 'content_block_delta':
                                yield json_chunk['delta']['text']
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Claude: {e}")
            yield None