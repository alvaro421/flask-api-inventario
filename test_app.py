import pytest
import sqlite3
import os
import tempfile
import json
from werkzeug.security import generate_password_hash

# Importaciones de la aplicación (asumiendo que están en el mismo nivel o accesibles)
from app import create_app 
from db_utils import get_db_connection 


# ----------------------------------------------------------------------
# FIXTURES (Inicialización de la App y la DB)
# ----------------------------------------------------------------------

@pytest.fixture
def app():
    """Configura la aplicación para pruebas, usa una base de datos temporal."""
    # 1. Creamos el archivo temporal y obtenemos el descriptor (db_fd) y la ruta (db_path)
    # Al usar tempfile.mkstemp(), el archivo existe en disco pero no tiene conexión abierta.
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'JWT_SECRET_KEY': 'clave-secreta-para-tests' 
    })

    # 2. Inicialización de la DB de prueba
    with app.app_context():
        # Obtenemos la conexión
        db = get_db_connection()
        
        # Creación de la tabla de usuarios
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL 
            );
        """)
        
        # Creación de la tabla de productos
        db.executescript("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)
        
        # Insertar un usuario de prueba (ID 1, contraseña 'testpassword')
        test_hash = generate_password_hash('testpassword')
        db.execute(
            "INSERT INTO usuarios (id, username, password_hash) VALUES (?, ?, ?)",
            (1, 'testuser', test_hash)
        )
        db.commit()

        # Insertar un producto de prueba (ID 100)
        db.execute(
            "INSERT INTO productos (id, nombre, cantidad, precio, usuario_id) VALUES (?, ?, ?, ?, ?)",
            (100, 'Laptop', 5, 1200.00, 1)
        )
        db.commit()
        
        # *** CRUCIAL para WinError 32: CERRAMOS LA CONEXIÓN DB inmediatamente después de usarla ***
        db.close() 

    # *** CRUCIAL para WinError 32: CERRAMOS EL DESCRIPTOR DEL ARCHIVO DEL SO ***
    os.close(db_fd)
    
    # 3. Devuelve la instancia de la aplicación al test
    yield app

    # 4. Limpieza: Borra la base de datos temporal después de que terminan los tests.
    try:
        os.unlink(db_path)
    except PermissionError:
        # Si el SO (Windows) todavía tiene un bloqueo, ignoramos el error.
        pass


@pytest.fixture
def client(app):
    """Cliente de prueba de Flask para hacer peticiones."""
    return app.test_client()

@pytest.fixture
def auth_header(client):
    """Obtiene un token JWT para el usuario de prueba y devuelve el encabezado Authorization."""
    response = client.post(
        '/auth/login',
        json={'username': 'testuser', 'password': 'testpassword'}
    )
    # Asumimos que el login debe devolver 201 y el token
    if response.status_code == 201:
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    raise Exception(f"Fallo al obtener token en fixture auth_header. Status: {response.status_code}. Data: {response.data.decode()}")


# ----------------------------------------------------------------------
# PRUEBAS DE LA RUTA DE AUTENTICACIÓN
# ----------------------------------------------------------------------

def test_auth_register_successful(client, app):
    """
    Prueba el registro exitoso de un nuevo usuario. 
    SINCRONIZADO: Espera el mensaje exacto: 'Usuario newuser registrado con exito'.
    """
    response = client.post(
        '/auth/register',
        json={'username': 'newuser', 'password': 'newpassword'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    
    # Sincronizado con el mensaje exacto de tu API
    assert 'mensaje' in data
    assert data['mensaje'] == 'Usuario newuser registrado con exito'
    
    # Verifica la inserción en la DB
    with app.app_context():
        db = get_db_connection()
        user = db.execute(
            'SELECT username FROM usuarios WHERE username = ?', ('newuser',)
        ).fetchone()
        db.close()
        assert user is not None

def test_auth_login_successful(client):
    """
    Prueba el inicio de sesión exitoso.
    SINCRONIZADO: Solo espera la clave 'access_token'.
    """
    response = client.post(
        '/auth/login',
        json={'username': 'testuser', 'password': 'testpassword'}
    )
    assert response.status_code == 201 
    data = json.loads(response.data)
    # Comprobación de que el token existe
    assert 'access_token' in data

def test_auth_whoami_successful(client, auth_header):
    """Prueba el endpoint protegido /auth/protected."""
    response = client.get('/auth/protected', headers=auth_header) 
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'logged_in_as' in data
    assert data['logged_in_as'] == '1' # ID del usuario de prueba

# ----------------------------------------------------------------------
# PRUEBAS DE LA RUTA DE PRODUCTOS
# ----------------------------------------------------------------------

def test_productos_get_list_authenticated(client, auth_header):
    """
    Prueba obtener la lista de productos con autenticación. 
    SINCRONIZADO: Tu API devuelve directamente una lista ([...]).
    """
    response = client.get('/productos/', headers=auth_header)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['nombre'] == 'Laptop'

def test_productos_get_list_unauthenticated(client):
    """Prueba obtener la lista de productos sin autenticación (debe fallar)."""
    response = client.get('/productos/')
    # Espera 401 (Unauthorized)
    assert response.status_code == 401

def test_productos_create_item_successful(client, app, auth_header):
    """
    Prueba la creación exitosa de un nuevo producto.
    SINCRONIZADO: Espera el mensaje exacto: "Producto agregado con exito".
    """
    new_product_data = {
        'nombre': 'Teclado Mecánico',
        'cantidad': 15,
        'precio': 99.99
    }
    response = client.post('/productos/', headers=auth_header, json=new_product_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['mensaje'] == 'Producto agregado con exito'
    assert 'id' in data

    # Verificamos la inserción en la base de datos
    with app.app_context():
        db = get_db_connection()
        product = db.execute(
            'SELECT nombre, cantidad, usuario_id FROM productos WHERE nombre = ?', ('Teclado Mecánico',)
        ).fetchone()
        db.close() 
        assert product is not None
        assert product['usuario_id'] == 1 

def test_productos_update_item_successful(client, auth_header):
    """
    Prueba la actualización exitosa de un producto existente (ID 100).
    Este test falla si no se corrigió el error de sintaxis del .get() en rutas/productos.py.
    """
    response = client.put('/productos/100', headers=auth_header, json={
        'nombre': 'Monitor Nuevo 4K',
        'cantidad': 10,
        'precio': 350.00
    }, follow_redirects=True)
    assert response.status_code == 200
    data = json.loads(response.data)
    # Tu API devuelve el objeto actualizado.
    assert data['nombre'] == 'Monitor Nuevo 4K'
    assert data['cantidad'] == 10

def test_productos_delete_item_successful(client, app, auth_header):
    """Prueba la eliminación exitosa de un producto."""
    # Insertar producto a eliminar (ID 101)
    with app.app_context():
        db = get_db_connection()
        db.execute("INSERT INTO productos (id, nombre, cantidad, precio, usuario_id) VALUES (?, ?, ?, ?, ?)",
                   (101, 'Webcam', 1, 50.00, 1))
        db.commit()
        db.close()

    response = client.delete('/productos/101', headers=auth_header, follow_redirects=True)
    # Espera 204 (No Content)
    assert response.status_code == 204
    
    # Verifica que se haya borrado
    with app.app_context():
        db = get_db_connection()
        product = db.execute(
            'SELECT * FROM productos WHERE id = 101'
        ).fetchone()
        db.close()
        assert product is None


def test_productos_delete_item_not_found(client, auth_header):
    """Prueba la eliminación de un producto que no existe."""
    response = client.delete('/productos/999', headers=auth_header, follow_redirects=True)
    # Espera 404 (Not Found)
    assert response.status_code == 404
