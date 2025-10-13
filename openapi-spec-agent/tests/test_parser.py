import os
import tempfile
import unittest
from src.parser import parse_file

class TestParser(unittest.TestCase):

    def test_parse_file_with_flask_route(self):
        # Create a temporary Python file with a Flask route
        content = """
from flask import Flask

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test_route():
    return "Hello, world!"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            temp_file_path = f.name

        # Parse the temporary file
        endpoints = parse_file(temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Assert that the endpoints are correct
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]["path"], "/test")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

if __name__ == "__main__":
    unittest.main()
