class BaseAIClient:
    def __init__(self, api_url, model):
        self.api_url = api_url
        self.model = model

    def get_response(self, prompt):
        raise NotImplementedError("Subclasses must implement get_response")
