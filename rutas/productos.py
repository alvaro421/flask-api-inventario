import sqlite3
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from db_utils import get_db_connection


logging.basicConfig(level=logging.INFO)

#creacion de blueprint
productos_bp = Blueprint('productos', __name__, url_prefix='/productos')
# --- CRUD para productos ---

@productos_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def handle_productos():
    db = get_db_connection()
    current_user_id = get_jwt_identity()
    try:
        user_id_int = int(current_user_id)
    except (TypeError, ValueError):
        logging.error("ID de usuario del token no es convertible a entero")
        return jsonify({"msg": "Error de autenticacion. ID de usuario invalido en el token."}), 401
    

    if request.method == 'GET':
        try:
            productos = db.execute(
                "SELECT id, nombre, cantidad, precio FROM productos WHERE usuario_id = ?",
                (user_id_int,)
            ).fetchall()
            return jsonify([dict(producto) for producto in productos]), 200
        except Exception as e:
            logging.error(f"Error al listar productos: {e}")
            return jsonify({"mensaje": "Error interno del servidor al obtener productos"}), 500
    
    #POST crear un nuevo producto
    elif request.method == 'POST':
        data = request.get_json()
        nombre = data.get('nombre')
        cantidad = data.get('cantidad')
        precio = data.get('precio')
        
        #validacion basico de datos de entrada
        if not nombre or cantidad is None or precio is None:
            return jsonify({"msg": "Faltan datos requeridos (nombre, cantidad, precio)"}), 400
        
        #validacion de tipo de datos (asegurar que sean los esperados
        if not isinstance(cantidad, int) or not isinstance(precio, (int, float)):
            return jsonify({"msg": "Cantidad debe ser un entero, el precio debe ser un numero"}), 400
        
        try:
            cursor = db.execute(
                "INSERT INTO productos (nombre, cantidad, precio, usuario_id) VALUES (?, ?, ?, ?)",
                (nombre, cantidad, precio, user_id_int)
            )
            db.commit()
            return jsonify({"mensaje": "Producto agregado con exito", "id": cursor.lastrowid}), 201
        except Exception as e:
            logging.error(f"Error al agregar producto: {e}")
            return jsonify({"mensaje": "Error interno del servidor al crear producto"}), 500
    

#obtener por ID, ACTUALIZAR Y ELIMINAR
@productos_bp.route('/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_producto_id(producto_id):
    db = get_db_connection()
    current_user_id = get_jwt_identity()

    try:
        user_id_int = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({"mensaje": "Error de autenticacion. ID de usuario invalido en el token."}), 401

    def get_producto(pid):
        return db.execute(
            "SELECT id, nombre, cantidad, precio, usuario_id FROM productos WHERE id = ? AND usuario_id = ?",
            (pid, user_id_int)
        ).fetchone()
    #comprobar la existencia del producto antes de cualquier operacion
    producto_existente = get_producto(producto_id)

    #GET obtener un producto especifico
    if request.method == 'GET':
        if producto_existente:
            prod_dict = dict(producto_existente)
            del prod_dict['usuario_id']
            return jsonify(prod_dict), 200
        return jsonify({"mensaje": "producto no encontrado o no autorizado"}), 404
    
    if not producto_existente:
        return jsonify({"mensaje": "producto no encontrado o no autorizado"}), 404



    #PUT actualizar un producto existente
    elif request.method == 'PUT':
        data = request.get_json()

        #valores del json si se proporcionan
        nombre = data.get('nombre', producto_existente['nombre'])
        cantidad = data.get('cantidad', producto_existente['cantidad'])
        precio = data.get('precio', producto_existente['precio'])

        if not data:
            return jsonify({"mensaje": "se requiere al menos un campo para actualizar (nombre, cantidad o precio)"}), 400
        try:
            cantidad_final = int(cantidad)
            precio_final = float(precio)
        except (TypeError, ValueError):
            return jsonify({"mensaje": "La cantidad debe ser un entero y el precio un numero"}), 400
        
        try:
            db.execute(
                "UPDATE productos SET nombre = ?, cantidad = ?, precio = ? WHERE id = ? AND usuario_id = ?",
                (nombre, cantidad_final, precio_final, producto_id, user_id_int)
            )
            db.commit()

            productio_actualizado = get_producto(producto_id)
            if productio_actualizado:
                prod_dict = dict(productio_actualizado)
                del prod_dict['usuario_id']
                return jsonify(prod_dict), 200
            
            return jsonify({"mensaje": "Producto actualizado con exito"}), 200
        except Exception as e:
            logging.error(f"Error al actualizar producto: {e}")
            return jsonify({"mensaje": "Error interno del servidor al actualizar"}), 500


    #DELETE eliminar un producto
    elif request.method == 'DELETE':
        try:
            db.execute("DELETE FROM productos WHERE id = ? AND usuario_id = ?", (producto_id, user_id_int))
            db.commit()
            return '', 204
        except Exception as e:
            logging.error(f"Error al eliminar producto: {e}")
            return jsonify({"mensaje": "Error interno del servidor al eliminar"}), 500
