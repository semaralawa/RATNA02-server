DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS movement;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE movement (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  move_name TEXT NOT NULL,
  act INTEGER
);