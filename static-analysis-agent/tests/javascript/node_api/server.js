/**
 * Node.js Express API server with intentional issues.
 */

const express = require('express');
const mysql = require('mysql');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Issue: hardcoded credentials
const DB_CONFIG = {
  host: 'localhost',
  user: 'root',
  password: 'password123',
  database: 'myapp'
};

// Issue: no input validation middleware
app.use(express.json());

// Security issue: SQL injection
app.get('/api/users/:id', (req, res) => {
  const connection = mysql.createConnection(DB_CONFIG);
  const userId = req.params.id;

  // Issue: direct string concatenation in SQL query
  const query = `SELECT * FROM users WHERE id = ${userId}`;

  connection.query(query, (error, results) => {
    if (error) {
      res.status(500).json({ error: error.message });
    } else {
      res.json(results);
    }
  });

  connection.end();
});

// Security issue: command injection
app.post('/api/execute', (req, res) => {
  const command = req.body.command;

  // Issue: executing user input directly
  exec(command, (error, stdout, stderr) => {
    if (error) {
      res.status(500).json({ error: error.message });
    } else {
      res.json({ output: stdout, error: stderr });
    }
  });
});

// Issue: path traversal vulnerability
app.get('/api/files/:filename', (req, res) => {
  const filename = req.params.filename;

  // Issue: no path validation
  const filePath = path.join(__dirname, 'files', filename);

  fs.readFile(filePath, 'utf8', (error, data) => {
    if (error) {
      res.status(404).json({ error: 'File not found' });
    } else {
      res.send(data);
    }
  });
});

// Issue: no rate limiting
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  // Issue: weak password validation
  if (username === 'admin' && password === 'admin123') {
    res.json({ token: 'fake-jwt-token' });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

// Issue: eval usage
app.post('/api/eval', (req, res) => {
  const code = req.body.code;

  try {
    // Security issue: eval with user input
    const result = eval(code);
    res.json({ result });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Issue: no CORS configuration
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Issue: unused function
function unusedHelper() {
  return 'This function is never used';
}

// Issue: global variable
global.appConfig = {
  debug: true,
  secret: 'hardcoded-secret'
};
