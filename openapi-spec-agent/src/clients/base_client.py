import requests
import json

class BaseAIClient:
    """Base class for AI clients."""
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model

    def get_response(self, prompt):
        """Sends a prompt to the AI API and yields the response chunks."""
        raise NotImplementedError("Subclasses must implement this method.")

def get_ai_client(client_name, model):
    """Factory function to get an AI client."""
    if client_name == "ollama":
        from .ollama_client import OllamaClient
        return OllamaClient(model=model)
    elif client_name == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient(model=model)
    elif client_name == "claude":
        from .claude_client import ClaudeClient
        return ClaudeClient(model=model)
    elif client_name == "cerebras":
        from .cerebras_client import CerebrasClient
        return CerebrasClient(model=model)
    elif client_name == "openrouter":
        from .openrouter_client import OpenRouterClient
        return OpenRouterClient(model=model)
    else:
        raise ValueError(f"Unknown AI client: {client_name}")