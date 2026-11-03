

CREATE DATABASE IF NOT EXISTS chikys_nails
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE chikys_nails;

CREATE TABLE IF NOT EXISTS clientes (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(150) NOT NULL,
    telefono  VARCHAR(30)  NOT NULL,
    correo    VARCHAR(150),
    direccion VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS personal (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    telefono     VARCHAR(30)  NOT NULL,
    especialidad VARCHAR(150) NOT NULL,
    carga        VARCHAR(30)  NOT NULL DEFAULT 'Disponible'
);

CREATE TABLE IF NOT EXISTS insumos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(150)   NOT NULL,
    categoria    VARCHAR(50)    NOT NULL,
    cantidad     DECIMAL(10,2)  NOT NULL DEFAULT 0,
    unidad       VARCHAR(30)    NOT NULL,
    stock_minimo DECIMAL(10,2)  NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS servicios (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nombre   VARCHAR(150)  NOT NULL,
    duracion INT           NOT NULL,
    precio   DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS servicio_insumos (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    servicio_id   INT NOT NULL,
    insumo_nombre VARCHAR(150)  NOT NULL,
    cantidad      DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS citas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cliente     VARCHAR(150) NOT NULL,
    servicio    VARCHAR(150) NOT NULL,
    personal    VARCHAR(150) NOT NULL,
    fecha       VARCHAR(10)  NOT NULL,
    hora        VARCHAR(5)   NOT NULL,
    duracion    INT          NOT NULL DEFAULT 0,
    completada  TINYINT(1)   NOT NULL DEFAULT 0
);
