# Proyecto de Gestión de Alquiler de Portátiles

Este proyecto es una aplicación web desarrollada con Flask para gestionar el alquiler de portátiles. Permite a los usuarios registrarse, iniciar sesión, alquilar portátiles disponibles y ver sus reservas. Los administradores pueden agregar, eliminar portátiles y ver todas las reservas realizadas.

## Requisitos

- Python 3.6+
- Flask
- PyMySQL
- Werkzeug

## Instalación

1.  Clonar el repositorio:

    ```bash
    git clone https://github.com/jcalderonvelo/prestamoPortatiles.git
    cd prestamoPortatiles
    ```

2.  Crear un entorno virtual (recomendado):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate  # En Windows
    ```

3.  Instalar las dependencias:

    ```bash
    pip install Flask pymysql Werkzeug
    ```

4.  Configurar la base de datos:

    -   Asegúrate de tener un servidor MySQL en ejecución.
    -   Crea una base de datos llamada `gr2_db`.
    -   Crea las tablas necesarias (ver esquema de la base de datos más abajo).
    -   Modifica la conexión a la base de datos en el archivo `app.py` con tus credenciales:

        ```python
        db = pymysql.connect(host='10.3.29.20', port=33060, user='user_gr2', password='portatil123', database='gr2_db')
        ```

5.  Ejecutar la aplicación:

    ```bash
    python app.py
    ```

    La aplicación estará disponible en `http://127.0.0.1:5000/`.

## Esquema de la Base de Datos

### Tabla `usuarios`

| Columna         | Tipo          | Descripción                               |
| --------------- | ------------- | ----------------------------------------- |
| `id`            | INT AUTO_INCREMENT | Identificador único del usuario         |
| `username`      | VARCHAR(255)  | Nombre de usuario                         |
| `email`         | VARCHAR(255)  | Correo electrónico del usuario            |
| `password_hash` | VARCHAR(255)  | Hash de la contraseña del usuario         |

### Tabla `portatiles`

| Columna         | Tipo          | Descripción                               |
| --------------- | ------------- | ----------------------------------------- |
| `id`            | INT AUTO_INCREMENT | Identificador único del portátil        |
| `marca`         | VARCHAR(255)  | Marca del portátil                        |
| `estado`        | VARCHAR(255)  | Estado del portátil                       |
| `almacenamiento`| VARCHAR(255)  | Capacidad de almacenamiento del portátil |
| `OS`            | VARCHAR(255)  | Sistema operativo del portátil            |
| `ram`           | VARCHAR(255)  | RAM del portátil                          |

### Tabla `reservas`

| Columna         | Tipo          | Descripción                               |
| --------------- | ------------- | ----------------------------------------- |
| `id`            | INT AUTO_INCREMENT | Identificador único de la reserva       |
| `usuario_id`    | INT           | Identificador del usuario que hizo la reserva |
| `portatil_id`   | INT           | Identificador del portátil reservado      |
| `fecha_reserva` | DATETIME      | Fecha y hora de la reserva                |

### Tabla `admin`

| Columna         | Tipo          | Descripción                               |
| --------------- | ------------- | ----------------------------------------- |
| `id`            | INT AUTO_INCREMENT | Identificador único del administrador   |
| `correo`        | VARCHAR(255)  | Correo electrónico del administrador      |
| `password`      | VARCHAR(255)  | Contraseña del administrador              |

### Tabla `fecha`

| Columna         | Tipo          | Descripción                               |
| --------------- | ------------- | ----------------------------------------- |
| `id`            | INT AUTO_INCREMENT | Identificador único de la fecha       |
| `id_portatiles` | INT           | Identificador del portátil reservado      |
| `fecha_reserva` | DATETIME      | Fecha y hora de la reserva                |

## Funcionalidades

### Usuarios

-   Registro de usuarios.
-   Inicio de sesión.
-   Visualización de portátiles disponibles.
-   Alquiler de portátiles.
-   Visualización de sus reservas.
-   Cancelación de reservas.
-   Visualización de la RAM de los portátiles reservados.
-   Visualización de la fecha actual.
-   Cierre de sesión.

### Administradores

-   Inicio de sesión de administrador.
-   Agregar nuevos portátiles (incluyendo RAM).
-   Eliminar portátiles y sus reservas asociadas.
-   Visualización de todas las reservas.
-   Visualización de todos los portátiles y sus estados.
-   Visualización de la RAM de los portátiles reservados.
-   Visualización de la fecha actual.
-   Cierre de sesión.

## Rutas

-   `/`: Página de inicio.
-   `/login`: Página de inicio de sesión de usuario.
-   `/register`: Página de registro de usuario.
-   `/dashboard`: Panel de control del usuario.
-   `/alquilar/<int:portatil_id>`: Ruta para alquilar un portátil.
-   `/cancelar_reserva/<int:reserva_id>`: Ruta para cancelar una reserva.
-   `/admin_login`: Página de inicio de sesión de administrador.
-   `/admin_dashboard`: Panel de control del administrador.
-   `/reservados`: Lista de portátiles reservados.
-   `/mis_reservas`: Lista de reservas del usuario.
-   `/logout`: Cierre de sesión.

## Seguridad

-   Las contraseñas de los usuarios se almacenan de forma segura utilizando `generate_password_hash` de Werkzeug.
-   Las sesiones se gestionan con Flask `session`.

## Notas

-   Este proyecto es una base y puede ser mejorado con más funcionalidades y mejoras de seguridad.
-   Los templates HTML se encuentran en la carpeta `templates`.
-   La conexión a la base de datos debe ser configurada correctamente.
-   Se ha añadido la funcionalidad de cancelar reservas para los usuarios y la visualización de la RAM de los portátiles.
-   Se ha añadido la funcionalidad de la fecha actual para el usuario y el administrador.
-   Se ha añadido la funcionalidad de la RAM para los portátiles.
