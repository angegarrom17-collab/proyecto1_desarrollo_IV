# proyecto1_desarrollo_IV
Sistema de gestión de ventas de productos de belleza. 


Tienda de Belleza

1. Descripción del proyecto

Este proyecto consiste en el desarrollo de una API REST para administrar una tienda de maquillaje, utilizando Python, Django y Django REST Framework.

El sistema permite gestionar clientes, productos, proveedores, cursos y facturas, relacionando los diferentes módulos para facilitar las operaciones de la tienda.

2. Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- MySQL
- Postman
- Visual Studio Code

3. Módulos del sistema

- Clientes: administración de los clientes registrados.
- Productos: gestión de productos, categorías y existencias.
- Proveedores: administración de proveedores.
- Cursos: gestión de cursos e inscripciones.
- Facturas: registro y consulta de facturas y sus detalles.

4. Pruebas automatizadas

Se implementaron 29 pruebas automatizadas utilizando las herramientas de pruebas de Django.

Para ejecutarlas:

python manage.py test

Resultado obtenido: 29 pruebas ejecutadas correctamente, sin errores ni fallos.

Configuracion de MySQL: 

--------CREACION ----------

CREATE DATABASE tienda_belleza_db
CHARACTER SET utf8mb4
collate utf8mb4_unicode_ci;

show databases;

CREATE USER 'tienda_belleza_user'@'localhost'
identified BY 'Belleza2026!';

GRANT ALL privileges
ON tienda_belleza_db.*
To 'tienda_belleza_user'@'localhost';
Flush Privileges;

use tienda_belleza_db;
SHOW TABLES; 

---------------------------------------------------------------------------
-Instalacion: MySQL - pip install python-dotenv - pip install mysqlclient
py -m venv .venv   -  .venv\Scripts\activate
python -m pip install "Django>=5.2,<5.3"
pip install djangorestframework

-Migraciones: python manage.py makemigrations - python manage.py migrate
-Crear usuario: python manage.py createsuperuser
-Configurar .env.example con los datos ingresados en MySQL
-Ejecucion: python manage.py runserver


---CATALOGO FINAL DE ENDPOINTS Y GUIA DE EJECUCION-

4. Catálogo final de endpoints

La API REST del sistema Tienda de Belleza permite realizar operaciones de consulta, registro, actualización y eliminación de información, según los permisos asignados a cada usuario.

URL base: "http://127.0.0.1:8000"

4.1. Autenticación

Método| Endpoint| Descripción
POST| "/api/token/"| Obtener un token de autenticación para acceder a la API.

4.2. Clientes

Método| Endpoint| Descripción
GET| "/api/clientes/"| Listar los clientes registrados.
POST| "/api/clientes/"| Registrar un nuevo cliente.
GET| "/api/clientes/{id}/"| Consultar un cliente específico.
PUT| "/api/clientes/{id}/"| Actualizar toda la información de un cliente.
PATCH| "/api/clientes/{id}/"| Actualizar parcialmente un cliente.
DELETE| "/api/clientes/{id}/"| Eliminar un cliente.

4.3. Productos

Método| Endpoint| Descripción
GET| "/api/productos/"| Listar los productos registrados.
POST| "/api/productos/"| Registrar un nuevo producto.
GET| "/api/productos/{id}/"| Consultar un producto específico.
PUT| "/api/productos/{id}/"| Actualizar toda la información de un producto.
PATCH| "/api/productos/{id}/"| Actualizar parcialmente un producto.
DELETE| "/api/productos/{id}/"| Eliminar un producto.
GET| "/api/productos/categorias/"| Listar las categorías de productos.
POST| "/api/productos/categorias/"| Registrar una categoría.
GET| "/api/productos/categorias/{id}/"| Consultar una categoría.
PUT| "/api/productos/categorias/{id}/"| Actualizar una categoría.
PATCH| "/api/productos/categorias/{id}/"| Actualizar parcialmente una categoría.
DELETE| "/api/productos/categorias/{id}/"| Eliminar una categoría.
GET| "/api/productos/estadisticas/"| Consultar estadísticas de productos.

4.4. Proveedores

Método| Endpoint| Descripción
GET| "/api/proveedores/"| Listar los proveedores registrados.
POST| "/api/proveedores/"| Registrar un proveedor.
GET| "/api/proveedores/{id}/"| Consultar un proveedor específico.
PUT| "/api/proveedores/{id}/"| Actualizar la información de un proveedor.
PATCH| "/api/proveedores/{id}/"| Actualizar parcialmente un proveedor.
DELETE| "/api/proveedores/{id}/"| Eliminar un proveedor.
GET| "/api/proveedores/entradas/"| Listar las entradas de productos.
POST| "/api/proveedores/entradas/"| Registrar una entrada de productos.
GET| "/api/proveedores/entradas/{id}/"| Consultar una entrada específica.

4.5. Cursos

Método| Endpoint| Descripción
GET| "/api/cursos/"| Listar los cursos disponibles.
POST| "/api/cursos/"| Registrar un nuevo curso.
GET| "/api/cursos/{id}/"| Consultar un curso específico.
PUT| "/api/cursos/{id}/"| Actualizar un curso.
PATCH| "/api/cursos/{id}/"| Actualizar parcialmente un curso.
DELETE| "/api/cursos/{id}/"| Eliminar un curso.
GET| "/api/cursos/{id}/inscripciones/"| Consultar las inscripciones de un curso.
POST| "/api/cursos/{id}/inscripciones/"| Registrar una inscripción.
GET| "/api/cursos/inscripciones/{id}/"| Consultar una inscripción específica.
PUT| "/api/cursos/inscripciones/{id}/"| Actualizar una inscripción.
PATCH| "/api/cursos/inscripciones/{id}/"| Actualizar parcialmente una inscripción.
DELETE| "/api/cursos/inscripciones/{id}/"| Eliminar una inscripción.
GET| "/api/cursos/estadisticas/"| Consultar estadísticas de cursos.

4.6. Facturas

Método| Endpoint| Descripción
GET| "/api/facturas/"| Listar las facturas registradas.
POST| "/api/facturas/"| Registrar una factura.
GET| "/api/facturas/{id}/"| Consultar una factura específica.
PUT| "/api/facturas/{id}/"| Actualizar una factura.
PATCH| "/api/facturas/{id}/"| Actualizar parcialmente una factura.
DELETE| "/api/facturas/{id}/"| Eliminar una factura.
GET| "/api/facturas/{id}/detalles/"| Consultar los detalles de una factura.
POST| "/api/facturas/{id}/detalles/"| Registrar un detalle de factura.
GET| "/api/facturas/detalles/{id}/"| Consultar un detalle específico.
DELETE| "/api/facturas/detalles/{id}/"| Eliminar un detalle de factura.
GET| "/api/facturas/estadisticas/"| Consultar estadísticas de facturación.

4.7. Códigos de respuesta HTTP

Código| Significado
200 OK| La solicitud se realizó correctamente.
201 Created| El registro se creó correctamente.
204 No Content| La operación se completó sin devolver contenido.
400 Bad Request| Los datos enviados son incorrectos o incumplen una validación.
401 Unauthorized| Se requiere autenticación válida.
403 Forbidden| El usuario no tiene permisos para realizar la operación.
404 Not Found| El recurso solicitado no existe.
409 Conflict| La operación presenta un conflicto con el estado actual del recurso.

4.8. Seguridad de los endpoints

El sistema utiliza autenticación por tokens y permisos según el tipo de usuario.

Las operaciones disponibles dependen de los permisos configurados en las vistas de Django REST Framework. Por esta razón, un usuario autenticado no necesariamente puede crear, modificar o eliminar todos los registros.

Para acceder a los endpoints protegidos desde Postman se debe incluir el encabezado:

"Authorization: Token TOKEN_OBTENIDO"

El sistema devuelve respuestas HTTP según el resultado de la solicitud y las validaciones correspondientes.



