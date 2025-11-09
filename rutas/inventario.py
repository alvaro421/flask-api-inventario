import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from rutas.db_utils import get_db_connection

# Define el Blueprint, el cual se registrará en app.py
bp = Blueprint('inventario', __name__, url_prefix='/')

# =========================================================================
# RUTAS PÚBLICAS Y PRINCIPALES (API Endpoints)
# =========================================================================

@bp.route('/api/productos', methods=['GET'])
def get_productos():
    """
    API Endpoint para obtener la lista de todos los productos (o los del usuario logueado).
    Devuelve un JSON con la lista de productos.
    """
    db = get_db_connection()
    productos = []
    
    if g.user:
        # Si hay un usuario logueado, trae SOLO sus productos
        db_results = db.execute(
            'SELECT id, nombre, cantidad, precio, usuario_id'
            ' FROM productos'
            ' WHERE usuario_id = ?'
            ' ORDER BY nombre ASC',
            (g.user['id'],)
        ).fetchall()
        
        # Convierte los objetos Row de la base de datos a diccionarios
        for row in db_results:
            productos.append(dict(row))
            
        return jsonify({
            'status': 'success',
            'user_id': g.user['id'],
            'data': productos
        })
    else:
        # Si no hay usuario logueado, puedes optar por:
        # 1. Devolver un error (opción recomendada para datos privados)
        return jsonify({
            'status': 'error',
            'message': 'No autorizado. Por favor inicie sesión o acceda a la ruta de autenticación.',
            'data': []
        }), 401 # 401 Unauthorized


# Tarea: La ruta principal '/' no está definida, para evitar el error 404
# la definiremos con un mensaje simple.
@bp.route('/')
def home():
    """Ruta de bienvenida simple para confirmar que la API está activa."""
    return jsonify({
        'status': 'API Active',
        'message': 'Bienvenido al servicio de API de Inventario. Use /api/productos para acceder a los datos.'
    })


# =========================================================================
# RUTAS AUXILIARES
# =========================================================================

# Esta función es un decorador que se usaría para proteger rutas
def login_required(view):
    """
    Decorador para asegurar que un usuario esté logueado antes de acceder a la vista.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # Si no hay usuario logueado, devuelve un error 401 JSON en lugar de redirigir a HTML
            return jsonify({
                'status': 'error',
                'message': 'Acceso requerido. Por favor inicie sesión.'
            }), 401
        return view(**kwargs)
    return wrapped_view

# Tareas pendientes (a implementar como API endpoints):
# 1. Implementar la ruta para CREAR producto (POST /api/productos)
# 2. Implementar la ruta para OBTENER UN producto por ID (GET /api/productos/<id>)
# 3. Implementar la ruta para ACTUALIZAR producto (PUT/PATCH /api/productos/<id>)
# 4. Implementar la ruta para ELIMINAR producto (DELETE /api/productos/<id>)
