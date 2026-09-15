import os

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "0311"),
    "database": os.getenv("DB_NAME", "biblioteca_db"),
}


class Database:
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
