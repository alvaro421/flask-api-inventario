#rutas/auth.py
import functools
import sqlite3
import logging
from flask import Blueprint, request, jsonify, g, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from db_utils import get_db_connection

logging.basicConfig(level=logging.INFO)
#creacion de blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"mensaje": "Nombre de usuario y contraseña son requeridos"}), 400
    #genera el hash de la contraseña
    password_hash = generate_password_hash(password)

    db = get_db_connection()


    try:
        db.execute(
            "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        db.commit()
        return jsonify({"mensaje": f"Usuario {username} registrado con exito"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"mensaje": f"El usuario {username} ya existe"}), 409
    except Exception as e:
        logging.error(f"Error al registrar usuario: {e}")
        return jsonify({"mensaje": "Error interno del servidor al registrar"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    db = get_db_connection()
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Faltan nombre de usuario o contraseña"}), 400

    try:
        user_record = db.execute(
            "SELECT id, username, password_hash FROM usuarios WHERE username = ?", (username,)
        ).fetchone()

        if user_record is None or not check_password_hash(user_record['password_hash'], password):
            return jsonify({"msg": "Credenciales invalidas (usuario no encontrado)"}), 401
        
        access_token = create_access_token(identity=str(user_record['id']))
        return jsonify(access_token=access_token), 201
    
    except Exception as e:
        logging.error(f"Error en la ruta de login: {e}")
        return jsonify({"msg": f"Error interno del servidor durante el login"}), 500

def token_required():
    def wrapper(fn):
        @functools.wraps(fn)
        @jwt_required()
        def decorated_view(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200
    

