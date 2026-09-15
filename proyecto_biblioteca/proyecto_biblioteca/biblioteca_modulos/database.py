import mysql.connector
from mysql.connector import Error

from .config import DB_CONFIG


class Database:
    """Pequeña capa de acceso parametrizado para la aplicación."""

    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(**DB_CONFIG)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def query(self, sql, params=(), fetch=True):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            if fetch:
                return cursor.fetchall()
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def count(self, table):
        result = self.query(f"SELECT COUNT(*) AS total FROM `{table}`")
        return result[0]["total"]


__all__ = ["Database", "Error"]
