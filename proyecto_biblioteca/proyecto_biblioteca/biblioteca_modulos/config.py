import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "0311"),
    "database": os.getenv("DB_NAME", "biblioteca_db"),
}

ADMIN_USER = os.getenv("APP_USER", "Admin1")
ADMIN_PASSWORD = os.getenv("APP_PASSWORD", "contraseña123")
ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "biblioteca.ico")

TABLES = {
    "Autores": {
        "table": "autores",
        "id": "id_autor",
        "columns": ["nombre", "nacionalidad"],
    },
    "Categorias": {
        "table": "categorias",
        "id": "id_categoria",
        "columns": ["nombre"],
    },
    "Editoriales": {
        "table": "editoriales",
        "id": "id_editorial",
        "columns": ["nombre", "ciudad"],
    },
    "Usuarios": {
        "table": "usuarios",
        "id": "id_usuario",
        "columns": ["nombres", "apellidos", "documento", "telefono", "correo", "direccion"],
    },
    "Libros": {
        "table": "libros",
        "id": "id_libro",
        "columns": ["titulo", "isbn", "anio_publicacion", "id_autor", "id_editorial", "id_categoria"],
    },
    "Prestamos": {
        "table": "prestamos",
        "id": "id_prestamo",
        "columns": ["id_usuario", "fecha_prestamo", "fecha_devolucion", "estado"],
    },
    "Detalle de prestamos": {
        "table": "detalle_prestamo",
        "id": "id_detalle",
        "columns": ["id_prestamo", "id_libro", "cantidad"],
    },
    "Auditoria": {
        "table": "auditoria",
        "id": "id_auditoria",
        "columns": ["tabla_afectada", "operacion", "id_registro", "fecha", "descripcion"],
        "readonly": True,
    },
}
