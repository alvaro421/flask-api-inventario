#API RESTful de Inventario Multi-Usuario con Flask, JWT y SQLite

Implementacion de las operaciones CRUD (Create, Read, Update, Delete) de productos mediante *endpoints* REST, utilizando Flask para el backend, **JSON Web (JWT)** para la autenticacion y **SQLite** como base de datos.


## Descripción del Proyecto

Esta API RESTful esta diseñada para la gestion de inventarios de productos en un entorno multi-usuario. Cada usuario registrado tiene su propio conjunto de datos aislado, garantizando que solo puedan ver, crear, actualizar y eliminar los productos que les pertenecen.

**Caracteristicas Clave:**
* **Autenticacion Segura:** Rutas de Registro (`/auth/register`) y Login (`/auth/login`) con gestion de tokens JWT.
* **Autorizacion por JWT:** Acceso a rutas de inventario (`/producto`) **protegida**.
* **Segregacion de Datos:** Los productos estan vinculados a un usuario `usuario_id`, asegurando la privacidad del inventario de cada cuenta.
* **Prueba Unitarias:** Implementacion robusta de pruebas usando `pytest` para verificar la funcionalidad de los *endpoints*.

---
## Tecnologias Utilizadas
* **Backend:** Python 3
* **Framework Web:** Flask
* **Seguridad:** JSON Web Tokens (JWT)
* **Testing:** `pytest`
* **Base de Datos:** SQLite3 (persistencia local)
* **Comunicacion:** JSON
---

## Estructura del Proyecto

El proyecto sigue una estructura modular para mantener la logica de negocio, las rutas y la configuracion separadas y faciles de mantener.


## Endpoints de Autenticacion y API

| Tipo de Ruta | Metodo | Ruta | Descripcion | Header Requerido |
| :---: | :---: | :--- | :--- | :--- |
| **AUTENTICACION** | `POST` | `/auth/register` | Crea una nueva cuenta de usuario. | Ninguno |
| **AUTENTICACION** | `POST` | `/auth/login` | Inicia sesion y genera un **JWT**. | Ninguno |
| **INVENTARIO** | `GET` | `/productos` | Obtiene la lista **SOLO** de los productos del usuario logueado | `Authorization: Bearer <TOKEN>` |
| **INVENTARIO** | `POST` | `/productos` | Crea un nuevo producto y lo asocia al usuario logueado, | `Autorization: Bearer <TOKEN>` |
| **INVENTARIO** | `PUT` | `/productos/<id>` | Actualiza un producto existente. | `Authorization: Bearer <TOKEN>` |
| **INVENTARIO** | `DELETE` | `/productos/<id>` | Elimina un producto. | `Authorization: Bearer <TOKEN>` |

---
## Instalacion y Ejecucion

### 1. Clonacion del Repositorio

```bash
git clone https://github.com/alvaro421/flask-api-inventario.git
cd flask-api-inventario
```

### 2 Instalacion de Dependencias
#Activar entorno virtual
# ...

# Instalar dependencias
```
pip install Flask Flask-JWT-Extended pytest
```
### 3 Ejecutar el Servidor
inicia la aplicacion de Flask
```
python app.py
```
###Ejecucion de Pruebas Unitarias
Para ejecutar las pruebas implementadas, simplemente usa pytest desde el directorio raiz del proyecto:
```
pytest
```
Esto correra las pruebas definidas en test_app.py y verificara que todos los endpoints protegidos y de autenticacion funcionen correctamente.

### Pruebas (ejemplo con cURL)
Para probar la API, debes seguir la secuencia de: 1. Registro (Register), 2. Inicio de Sesion (Login) para detener el token, y 3. Usar ese token en las rutas protegidas.

### 1. Registrar un Nuevo Usuario (POST /auth/register)
```
curl -X POST http://127.0.0.1:5000/auth/register \
-H "Content-Type: application/json" \
-d '{"username": "user_prueba", "password": "secure-password-123"}'
```

### 2 Iniciar Sesion y Obtener el Token (POST /auth/login)
```
curl -X POST http://127.0.0.1:5000/auth/login \
-H "Content-Type: application/json" \
-d '{"username": "user_prueba", "password": "secure-password-123"}'
# guarda el access_token devuelta en una variable para los siguientes pasos
```

### 3. Crear Producto (POST/productos)
Reemplaza <TU_JWT_TOKEN> con el token que obtuviste en el paso 2
```
curl -X POST http://127.0.0.1:5000/productos \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <TU_JWT_TOKEN>" \
-d '{"nombre": "Monitor Gamer", "cantidad": 5, "precio": 350.99}'
```

### 4. Listar Productos del Usuario (GET/productos)
```
curl -X GET http://127.0.0.1:5000/productos \
-H "Authorization: Bearer <TU_JWT_TOKEN>" \
```

### 5. Obtener un producto ID (GET/<id>)
(Asume que el ID 1 ya existe)
```
curl -X GET http://127.0.0.1:5000/productos/1 \
-H "Authorization: Bearer <TU_JWT_TOKEN>" \
```

### 6. Actualizar un producto (PUT/<id>)
(Actualiza el producto con ID 1)
```
curl -X GET http://127.0.0.1:5000/productos/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <TU_JWT_TOKEN>" \
-d '{"nombre": "Monitor 4K (actualizado)", "cantidad": 3, "precio":400.00}'
```

### 7 Eliminar un producto (DELETE/<id>)
(Elimina el producto con el ID 2)
```
curl -X DELETE http://127.0.0.1:5000/productos/2 \
-H "Authorization: Bearer <TU_JWT_TOKEN>" \
