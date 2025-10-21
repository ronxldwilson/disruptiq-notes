import requests
import json
import os
import logging
from .base_classes import BaseAIClient
from .base_client import ContextExceeded

logging.basicConfig(level=logging.INFO)

class CerebrasClient(BaseAIClient):
    """AI client for Cerebras."""
    def __init__(self, model, api_url="https://api.cerebras.ai/v1/chat/completions"):
        super().__init__(api_url, model)
        self.api_key = os.environ.get("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable not set.")

    def get_response(self, prompt):
        """Sends a prompt to the Cerebras API and yields the response chunks."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with requests.post(self.api_url, headers=headers, json=data, stream=True) as response:
                    if response.status_code == 429:
                        logging.info(f"Rate limit exceeded, switching to next client...")
                        yield None
                        return
                    elif response.status_code == 400:
                        if 'context_length_exceeded' in response.text:
                            raise ContextExceeded(f"Context length exceeded for {self.model}")
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                            logging.warning(f"400 Bad Request (attempt {attempt + 1}/{max_retries}). Response: {response.text}. Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            logging.error(f"400 Bad Request after {max_retries} attempts. Response: {response.text}")
                            yield None
                            return
                    elif response.status_code != 200:   
                        logging.error(f"Unexpected status code {response.status_code}. Response: {response.text}")
                        yield None
                        return
                    response.raise_for_status()
                    for chunk in response.iter_lines():
                        if chunk:
                            decoded_chunk = chunk.decode('utf-8')
                            if decoded_chunk.startswith('data: '):
                                json_chunk = json.loads(decoded_chunk[6:])
                                if 'choices' in json_chunk and json_chunk['choices'][0].get('delta', {}).get('content'):
                                    yield json_chunk['choices'][0]['delta']['content']
                    break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Request exception (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Request failed after {max_retries} attempts: {e}")
                    yield None