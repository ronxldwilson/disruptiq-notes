#!/usr/bin/env python3
import json

# Dummy output for testing
output = {
    "type": "test_map",
    "data": ["item1", "item2"],
    "status": "success"
}

print(json.dumps(output))
