import requests
import json
import os
import logging
from .base_classes import BaseAIClient

logging.basicConfig(level=logging.INFO)

class GeminiClient(BaseAIClient):
    """AI client for Google Gemini."""
    def __init__(self, model, api_url="https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set.")
        super().__init__(api_url, model)

    def get_response(self, prompt):
        """Sends a prompt to the Gemini API and yields the response chunks."""
        url = self.api_url.format(model=self.model) + "?key=" + self.api_key
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7}
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with requests.post(url, json=data, stream=True) as response:
                    if response.status_code == 429:
                        logging.info(f"Rate limit exceeded, switching to next client...")
                        yield None
                        return
                    elif response.status_code == 400:
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt
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
                    # Gemini streaming is different; for simplicity, assume non-streaming for now
                    result = response.json()
                    if 'candidates' in result and result['candidates']:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        yield text
                    else:
                        yield ""
                    break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logging.warning(f"Request exception (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Request failed after {max_retries} attempts: {e}")
                    yield None
