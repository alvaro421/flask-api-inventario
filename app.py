from flask import Flask, jsonify, request
import sqlite3

#inicializar la apliacion Flask
app = Flask(__name__)

#configuracion de la base de datos
NOMBRE_BD = 'inventario.db'

#------------------------
#1 conexion a la bd
def get_db_connection():
    conn = sqlite3.connect(NOMBRE_BD)
    conn.row_factory = sqlite3.Row # permitte acceder a las columnas por nombre
    return conn

#---------------------
#2 ruta principal (para probar uqe el servidor funciona)
@app.route('/productos', methods=['GET'])
def listar_productos():
    conn = get_db_connection()

    productos_db = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()

    #convertir a una lista de diccionario para JSON
    productos_json = []
    for producto in productos_db:
        productos_json.append(dict(producto))

    # usar jsonify para devolver la lista como respuesta JSON
    return jsonify(productos_json)

@app.route('/productos', methods=['POST'])
def crear_producto():
    # obtener los datos enviados por el cliente en formato JSON
    datos_recibidos = request.json

    #extraer los campos requeridos
    nombre = datos_recibidos['nombre']
    cantidad = datos_recibidos['cantidad']
    precio = datos_recibidos['precio']

    #conexion e incercion
    conn = get_db_connection()
    cursor = conn.cursor()

    #insert

    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
        (nombre, cantidad, precio)
    )
    nuevo_id = cursor.lastrowid
    conn.commit()
    conn.close()

    #devolver una respues JSON con el producto creado
    return jsonify({
        'id': nuevo_id,
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio
    }), 201 #201 es el codigo HTTP que significa Created

@app.route('/productos/<int:id_producto>', methods=['PUT'])
def actulizar_producto(id_producto):
    #1 obtener los datos (del cuerpo JSON de la peticion)
    datos_recibidos =request.json

    #manejar el caso en que el precio o la cantidad no se envien
    nueva_cantidad = datos_recibidos.get('cantidad')
    nuevo_precio =datos_recibidos.get('precio')

    #2 validacion simple
    if nueva_cantidad is None or nuevo_precio is None:
        return jsonify({'error': 'faltan datos de cantidad o precio.'}), 400
    

    #3 conexion y actualizacion
    conn =get_db_connection()
    cursor = conn.cursor()

    #comandos SQL
    cursor.execute(
        "UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?",
        (nueva_cantidad, nuevo_precio, id_producto)
    )
    filas_afectadas = cursor.rowcount
    conn.commit()
    conn.close()

    #4 respuesta
    if filas_afectadas == 0:
        return jsonify({'mensaje': f'producto ID {id_producto} no encontrado para actualizar.'}), 404
    else:
        return jsonify({
            'mensaje' : f'producto ID {id_producto} actualizado correctamente.',
            'id': id_producto,
            'cantidad' : nueva_cantidad,
            'precio' : nuevo_precio
        })

@app.route('/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    #conexion a la base de datos
    conn =get_db_connection()
    cursor = conn.cursor()

    #delete
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()
    
    filas_afectadas = cursor.rowcount #cuenta filas eliminadas

    #respuesta
    if filas_afectadas == 0:
        #devuelve not found si el ID no existia
        return jsonify({'mensaje' : f'producto ID {id_producto} no encontrado para eliminar.'}), 404
    else:
        #devuelve un 200 (ok) mensaje de exito
        return jsonify({'mensaje' : f'producto ID {id_producto} eliminado correctamente.'}), 200


def index():
    return"servidor Flask del inventario funcionando"

#------------------------
#3 mantener la base de datos
def inicializador_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    #limpiamos estructura
    cursor.execute("DROP TABLE IF EXISTS productos")
    cursor.execute("""
    CREATE TABLE productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL)
    
    """)
    conn.commit()
    conn.close()

#-------------------------
#4 punto de arranque
if __name__ == '__main__':
    inicializador_db()

    #ejecutar la aplicacion en modo debuh(para desarrollo
    app.run(debug=True)