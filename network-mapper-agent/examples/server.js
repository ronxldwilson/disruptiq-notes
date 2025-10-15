const express = require('express');
const app = express();
const cors = require('cors');

app.use(cors({origin: '*'}));

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
