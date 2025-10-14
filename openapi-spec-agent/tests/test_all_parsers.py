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

    def test_typescript_nextjs_parser(self):
        content = """
import type { NextApiRequest, NextApiResponse } from 'next'

type ResponseData = {
  message: string
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method === 'POST') {
    res.status(200).json({ message: 'Hello from Next.js!' })
  } else {
    res.status(200).json({ message: 'Hello from Next.js!' })
  }
}
"""
        # create a temp file in a nested directory to simulate the pages/api structure
        temp_dir = tempfile.mkdtemp()
        self.temp_files.append(temp_dir)
        api_dir = os.path.join(temp_dir, "pages", "api")
        os.makedirs(api_dir)
        temp_file = self._create_temp_file(content, os.path.join(api_dir, "hello.ts"))

        endpoints = parse_file(temp_file)
        self.assertGreater(len(endpoints), 0, "TypeScript Next.js parser failed to find endpoints")
        self.assertEqual(endpoints[0]["path"], "/hello")
        self.assertEqual(endpoints[0]["methods"], ["POST", "GET"])

if __name__ == "__main__":
    unittest.main()
