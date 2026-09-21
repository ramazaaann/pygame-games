DROP TABLE IF EXISTS phones;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS groups;

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    birthday DATE,
    group_id INT REFERENCES groups(id)
);

CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    contact_id INT REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

INSERT INTO groups(name)
VALUES
('Family'),
('Work'),
('Friend'),
('Other');