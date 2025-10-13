import os
import unittest
import importlib
import sys
import tempfile

# Add project root to sys.path so we can import src as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.parser import parse_file
sys.path.pop(0)  # Remove project root from path

class TestAllParsers(unittest.TestCase):

    def setUp(self):
        self.temp_files = []

    def tearDown(self):
        for f in self.temp_files:
            os.remove(f)

    def _create_temp_file(self, content, suffix):
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            temp_file_path = f.name
        self.temp_files.append(temp_file_path)
        return temp_file_path

    def test_csharp_aspnetcore_parser(self):
        content = """
using Microsoft.AspNetCore.Mvc;

namespace MyNamespace.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class MyController : ControllerBase
    {
        [HttpGet]
        public IEnumerable<string> Get()
        {
            return new string[] { "value1", "value2" };
        }

        [HttpPost]
        public void Post([FromBody] string value)
        {
        }
    }
}
"""
        temp_file = self._create_temp_file(content, ".cs")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "CSharp ASP.NET Core parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/My")
        self.assertEqual(endpoints[0]["methods"], ["GET"])
        self.assertEqual(endpoints[1]["path"], "/My")
        self.assertEqual(endpoints[1]["methods"], ["POST"])

    def test_go_gin_parser(self):
        content = """
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "pong",
        })
    })
    r.POST("/users", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "user created",
        })
    })
    r.Run() // listen and serve on 0.0.0.0:8080
}
"""
        temp_file = self._create_temp_file(content, ".go")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Go Gin parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/ping")
        self.assertEqual(endpoints[0]["methods"], ["GET"])
        self.assertEqual(endpoints[1]["path"], "/users")
        self.assertEqual(endpoints[1]["methods"], ["POST"])

    def test_java_jaxrs_parser(self):
        content = """
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

@Path("/myresource")
public class MyResource {

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String getIt() {
        return "Got it!";
    }
}
"""
        temp_file = self._create_temp_file(content, ".java")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Java JAX-RS parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/myresource")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_java_springboot_parser(self):
        content = """
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MyController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }
}
"""
        temp_file = self._create_temp_file(content, ".java")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Java Spring Boot parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/hello")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_javascript_express_parser(self):
        content = """
const express = require('express');
const app = express();

app.get('/api/data', (req, res) => {
  res.send('Hello from Node.js!');
});
"""
        temp_file = self._create_temp_file(content, ".js")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "JavaScript Express parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/api/data")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_javascript_nextjs_parser(self):
        content = """
export default function handler(req, res) {
  res.status(200).json({ name: 'John Doe' });
}
"""
        temp_file = self._create_temp_file(content, ".js")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "JavaScript Next.js parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_python_django_parser(self):
        content = """
from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.article_list, name='article-list'),
]
"""
        temp_file = self._create_temp_file(content, ".py")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Python Django parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "articles/")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_python_fastapi_parser(self):
        content = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return {"message": "Hello FastAPI"}
"""
        temp_file = self._create_temp_file(content, ".py")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Python FastAPI parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/items/")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_python_flask_parser(self):
        content = """
from flask import Flask

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test_route():
    return "Hello, world!"
"""
        temp_file = self._create_temp_file(content, ".py")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Python Flask parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/test")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

    def test_ruby_rails_parser(self):
        content = """
Rails.application.routes.draw do
  get 'welcome/index'
  resources :articles
end
"""
        temp_file = self._create_temp_file(content, ".rb")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "Ruby Rails parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/welcome/index")
        self.assertEqual(endpoints[0]["methods"], ["GET"])
        self.assertEqual(endpoints[1]["path"], "/articles")
        self.assertEqual(endpoints[1]["methods"], ["GET"])
        self.assertEqual(endpoints[2]["path"], "/articles")
        self.assertEqual(endpoints[2]["methods"], ["POST"])
        self.assertEqual(endpoints[3]["path"], "/articles/{id}")
        self.assertEqual(endpoints[3]["methods"], ["GET"])
        self.assertEqual(endpoints[4]["path"], "/articles/{id}")
        self.assertEqual(endpoints[4]["methods"], ["PUT", "PATCH"])
        self.assertEqual(endpoints[5]["path"], "/articles/{id}")
        self.assertEqual(endpoints[5]["methods"], ["DELETE"])

    def test_typescript_nestjs_parser(self):
        content = """
import { Controller, Get } from '@nestjs/common';

@Controller('cats')
export class CatsController {
  @Get()
  findAll(): string[] {
    return ['hello', 'world'];
  }
}
"""
        temp_file = self._create_temp_file(content, ".ts")
        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "TypeScript NestJS parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/cats")
        self.assertEqual(endpoints[0]["methods"], ["GET"])

if __name__ == "__main__":
    unittest.main()
