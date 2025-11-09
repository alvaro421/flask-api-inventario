-- archivo para inicializar la base de datos (SQLite)

-- tabla para usuarios

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NO NULL
);

--tabla para productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    stock INTEGER NOT NULL
);

--inicializar un usuario de prueba (contraseña: mi_clave_secreta)

INSERT OR IGNORE INTO usuarios (username, password_hash) VALUES (
    'tester',
    '$2b$12$0tO/5lY4k2f7uLqM2T/lO.cE0h6W5f7uO0yT2k/lO.cE0h6W5f7u'
);

--datos iniciales de prueba para productos
INSERT OR IGNORE INTO productos (id, nombre, descripcion, precio, stock) VALUES
    (1, 'Laptop Gaming X500', 'Potente laptop para juegos con RTX 4080', 1500.00, 5),
    (2, 'Monitor Curvo 32"', 'Monitor 4K curvo de 144Hz', 450.00, 10);
