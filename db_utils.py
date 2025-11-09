import sqlite3
from flask import current_app, g

DATABASE = 'instance/proyecto_flask.sqlite'

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#funcion de inicializacion
def init_db(app):
    with app.app_context():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)

        db.commit()


def init_app_db(app):
    app.teardown_appcontext(close_db)
    init_db(app)