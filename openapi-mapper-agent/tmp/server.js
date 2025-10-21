const express = require('express');
const app = express();
const port = 3000;

app.get('/api/data', (req, res) => {
  res.send('Hello from Node.js!');
});

app.post('/api/users', (req, res) => {
  res.send('Create a new user');
});

app.listen(port, () => {
  console.log(`Express app listening at http://localhost:${port}`);
});
