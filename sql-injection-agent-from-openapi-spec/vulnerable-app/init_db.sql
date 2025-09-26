
-- init_db.sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  email TEXT,
  password TEXT
);
INSERT INTO users (username, email, password) VALUES ('alice', 'alice@example.com', 'password123');
INSERT INTO users (username, email, password) VALUES ('bob', 'bob@example.com', 'secret456');
