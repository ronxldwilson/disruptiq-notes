import json
import os
from pathlib import Path

class Config:
    def __init__(self, config_path=None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "default_config.json"
        self.settings = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
