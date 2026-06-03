CREATE DATABASE usuários

USE usuários

CREATE TABLE usuários (
login VARCHAR(100) NOT NULL,
senha VARCHAR(100) NOT NULL
);

SELECT * FROM usuários

INSERT INTO usuários (login, senha)
VALUES ('admin', '1234');

INSERT INTO usuários (login, senha)
VALUES ('useários', '5678')