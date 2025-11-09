from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({
        'status': 'API Active',
        'message': 'Bienvenido al servicio de API de Inventario. Los endpoints de productos inician en /productos.'
    })