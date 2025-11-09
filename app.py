import sqlite3
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
#importar blueprints
from db_utils import get_db_connection, init_app_db
from rutas.auth import auth_bp
from rutas.productos import productos_bp
from rutas.main import main_bp


load_dotenv()

    
def create_app(test_config=None):
    server  = Flask(__name__, instance_relative_config=True)
    #configuracion de claves
    jwt_secret = os.environ.get("JWT_SECRET_KEY")
    server.config["JWT_SECRET_KEY"] = jwt_secret if jwt_secret else "super-secreto-key-para-desarrollo"
    
    #2 configuracion de la DB
    server.config['DATABASE'] = os.environ.get("DATABASE_PATH", "inventario.db")

    #si se proporciona config de prueba, lo actualizamos
    if test_config is not None:
        server.config.from_mapping(test_config)

    #3 inicializamos JWT Manager
    jwt = JWTManager(server)

    #6 registrar blueprints
    server.register_blueprint(main_bp)
    server.register_blueprint(auth_bp, url_prefix='/auth')
    server.register_blueprint(productos_bp, url_prefix='/productos')


    #manejor de errores
    @server.errorhandler(404)
    def not_found(error):
        return jsonify({"msg": "Ruta no encontradoa"}), 404
    
    return server

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)