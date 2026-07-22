CREATE DATABASE almoxarifado;

USE almoxarifado;

CREATE TABLE estoque (
	id INT PRIMARY KEY auto_increment,
    nome VARCHAR(255),
    categoria VARCHAR(255),
    funcao VARCHAR(255),
    quantidade INT,
    valor DECIMAL,
	foto VARCHAR(255)
    );

CREATE TABLE usuarios (
	id INT PRIMARY KEY auto_increment,
    usuario VARCHAR(255),
    senha VARCHAR(255),
    funcao VARCHAR(10)
    );
    
INSERT INTO estoque(nome, categoria, funcao, quantidade, valor, foto)
VALUES ('teste', 'teste', 'teste', 10, 10, 'linkdeteste') ; 

SELECT * FROM estoque;
SELECT * FROM usuarios;
DELETE FROM estoque 
WHERE id = 3;