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

    def test_parse_file_with_express_route(self):
        # Create a temporary JavaScript file with an Express route
        content = """
const express = require('express');
const app = express();

app.get('/api/data', (req, res) => {
  res.send('Hello from Node.js!');
});

app.post('/api/users', (req, res) => {
  res.send('Create a new user');
});
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(content)
            temp_file_path = f.name

        # Parse the temporary file
        endpoints = parse_file(temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Assert that the endpoints are correct
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0]["path"], "/api/data")
        self.assertEqual(endpoints[0]["methods"], ["GET"])
        self.assertEqual(endpoints[1]["path"], "/api/users")
        self.assertEqual(endpoints[1]["methods"], ["POST"])

    def test_parse_file_with_django_urls(self):
        # Create a temporary Python file with Django URL patterns
        content = """
from django.urls import path

urlpatterns = [
    path('articles/', views.article_list, name='article-list'),
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),
    path('users/', views.user_list, name='user-list'),
]
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix="urls.py", delete=False) as f:
            f.write(content)
            temp_file_path = f.name

        # Parse the temporary file
        endpoints = parse_file(temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Assert that the endpoints are correct
        self.assertEqual(len(endpoints), 3)
        self.assertEqual(endpoints[0]["path"], "articles/")
        self.assertEqual(endpoints[0]["methods"], ["GET"])
        self.assertEqual(endpoints[1]["path"], "articles/{param}/")
        self.assertEqual(endpoints[1]["methods"], ["GET"])
        self.assertEqual(endpoints[2]["path"], "users/")
        self.assertEqual(endpoints[2]["methods"], ["GET"])

if __name__ == "__main__":
    unittest.main()
