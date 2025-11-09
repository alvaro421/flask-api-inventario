import pytest
import os
import tempfile
import sqlite3
# !!! CORRECCIÓN: Importamos desde 'app' en lugar de 'server'
from app import create_app, init_db, get_db_connection 

# Fixture para la aplicación de Flask (app)
@pytest.fixture
def app():
    # 1. Creamos un archivo temporal para la base de datos de prueba
    db_fd, db_path = tempfile.mkstemp()

    # 2. Creamos la aplicación de Flask con configuración de prueba
    test_config = {
        'TESTING': True,
        'DATABASE': db_path,
        # Usamos una clave JWT simple para pruebas
        'JWT_SECRET_KEY': 'test-secret-key'
    }
    flask_app = create_app(test_config)

    # 3. Inicializamos la base de datos de prueba
    with flask_app.app_context():
        # Llama a init_db para crear las tablas
        init_db(flask_app)
        
        # Opcional: crea un usuario de prueba para que 'auth_token' pueda loguearse
        db = get_db_connection()
        cursor = db.cursor()
        
        # Contraseña 'testpassword' hasheada (dummy)
        # Nota: En tu app real, usa el hash real de la contraseña
        hashed_password = 'pbkdf2:sha256:600000$P8g11rRz$1c8a7b1f3c5e0d4b6f7a8e9d2c3b4a5d6e7f8c9b0a1e2d3c4f5e6b7a8d9c0b1a' 
        
        try:
             cursor.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                ("testuser", "testpassword") 
             )
             db.commit()
        except sqlite3.IntegrityError:
            pass 

    # 4. Devuelve la aplicación
    yield flask_app

    # 5. Código de limpieza (Se ejecuta después de todas las pruebas)
    os.close(db_fd)
    os.unlink(db_path)

# Fixture para el cliente de prueba de Flask (client)
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture para obtener un token de autenticación (auth_token)
@pytest.fixture
def auth_token(client):
    # Petición de login para el usuario de prueba creado en la fixture 'app'
    response = client.post(
        '/auth/login',
        json={'username': 'testuser', 'password': 'testpassword'}
    )

    # Verifica que el login fue exitoso y devuelve el token
    if response.status_code == 200:
        return response.get_json()['access_token']
    else:
        # En caso de fallo (no debería pasar si 'app' fixture funciona)
        raise Exception(f"Failed to get auth token. Status: {response.status_code}. Data: {response.data.decode()}")
