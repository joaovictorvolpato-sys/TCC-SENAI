CREATE DATABASE IF NOT EXISTS almoxarifado;

USE almoxarifado;

CREATE TABLE IF NOT EXISTS estoque (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255),
    categoria VARCHAR(255),
    funcao VARCHAR(255),
    quantidade INT,
    valor DECIMAL(10,2),
    foto VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario VARCHAR(255) UNIQUE,
    senha VARCHAR(255),
    funcao VARCHAR(50)
);
