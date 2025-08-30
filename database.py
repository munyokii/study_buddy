"""Database connections and interaction functions"""
import mysql.connector
from mysql.connector import Error
from config import Config


class DatabaseManager:
    """Handles database connections and queries."""
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME
         }

    def create_connection(self):
        """Database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f'Error connecting to database: {e}')
            return None
