Implementacion de las operaciones CRUD (Create, Read, Update, Delete) de productos mediante endpoints REST, utilizando Flask para el backend y SQLite como base de datos local.

#API RESTful CRUD de Inventario

## Descripción del Proyecto

Esta es una **API RESTful** sencilla para la gestion de productos de inventario, implementando las **4 operaciones CRUD** (Crear, Leer, Actualizar, Eliminar).
El objetivo principal es demostrar habilidades en la construccion de servicios backend, manejo de bases de datos relacionales y la exposicion de datos mediante endpoints HTTP estandarizados.

---
## Tecnologias Utilizadas
* **Backend** Python 3
* **Framework Web:** Flask
* **Base de Datos:** SQLite3 (persistencia local)
* **Comunicacion:** JSON
---
##Endpoints de la API (CRUD)
la API opera sobre la ruta '/productos' y utiliza los siguiente metodos HTTP:
| Metodo | Ruta | Descripcion | Datos de Entrada (JSON) |
| :--: | :--: | :--: | :--: |
| **GET** | '/productos' | obtiene la lista completa de todos los productos. | *Ninguno* |
| **GET** | '/productos/<id>' | obtiene los detalles de un producto especifico por su ID | *Ninguno* |
|**POST** | '/productos' | **Crea** un nuevo producto en la base de datos. | '{"nombre": "...", "cantidad": ..., "precio": ...}' |
| **PUT** | '/productos/<id>' | **Actualiza** completamente un producto existente por su ID | '{"nombre": "...", "cantidad": ..., "precio": ...}' |
| **DELETE** | '/productos/<id>' | **Elimina** un producto especifico de la base de datos. | *Ninguno* |

---
## Pruebas (Ejemplo con cURL)
Para probar la API, podes usar 'curl' desde la terminal (asumiendo que el servidor Flask esta corriendo en 'http://127.0.0.1:5000'):
### 1. Crear producto (POST)
```bash
curl -X POST - H "Content-Type: application/json" -d '{"nombre": "Monitor Gamer", "cantidad": 5, "precio": 350.50}' http://127.0.0.1:5000/productos
```

## Listar productos (GET)
```
curl [http://127.0.0.1:5000/productos](http://127.0.0.1:5000/productos)```

## Eliminar producto ID 1 (DELETE)
```
curl -X DELETE [http://127.0.0.1:5000/productos/1](http://127.0.0.1:5000/productos/1)
```

## instalacion y ejecucion
**Clonacion**
git clone [https://github.com/alvaro421/flask-api-inventario.git]
cd flask-api-inventario

**instalar dependencias**
pip install Flask

**ejecutar el servidor**
python app.py
