CREATE TABLE User (
    id INT PRIMARY KEY,
    username VARCHAR,
    FOREIGN KEY (id) REFERENCES Post(id),
    FOREIGN KEY (id) REFERENCES Friend(id),
    FOREIGN KEY (id) REFERENCES Friend(id),
    FOREIGN KEY (id) REFERENCES Comment(id),
    FOREIGN KEY (id) REFERENCES Like(id)
);

CREATE TABLE Post (
    id INT PRIMARY KEY,
    author INT NOT NULL,
    FOREIGN KEY (id) REFERENCES Comment(id)
);

CREATE TABLE Friend (
    id INT PRIMARY KEY,
    self INT NOT NULL,
    other INT NOT NULL
);

CREATE TABLE Comment (
    id INT PRIMARY KEY,
    post INT NOT NULL,
    author INT
);

CREATE TABLE Like (
    id INT PRIMARY KEY,
    post INT,
    user INT NOT NULL,
    comment INT
);
