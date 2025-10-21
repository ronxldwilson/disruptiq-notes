import requests
import json
from .base_classes import BaseAIClient

# Add shared exception here so other client modules and ai_model can import it
class ContextExceeded(Exception):
    """Raised when an AI client's context/limit is exceeded."""
    pass

def get_ai_client(client_name, model):
    """Factory to return the requested AI client. Use lazy imports to avoid circular imports."""
    client_name = client_name.lower()
    if client_name in ("cerebras", "cerebrasai", "cerebras_client"):
        # Local import to avoid circular import at module import time
        from .cerebras_client import CerebrasClient
        return CerebrasClient(model)
    elif client_name in ("openai", "openai_client"):
        from .openai_client import OpenAIClient
        return OpenAIClient(model)
    elif client_name == "claude":
        from .claude_client import ClaudeClient
        return ClaudeClient(model=model)
    elif client_name == "gemini":
        # Default to a valid Gemini model if not specified or if it's the Ollama default
        if not model or model == "llama3.2":
            model = "gemini-2.5-flash"
        from .gemini_client import GeminiClient
        return GeminiClient(model=model)
    elif client_name == "openrouter":
        from .openrouter_client import OpenRouterClient
        return OpenRouterClient(model=model)
    else:
        raise ValueError(f"Unknown client: {client_name}")