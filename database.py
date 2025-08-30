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

    def initialize_database(self):
        """Function to create database and tables if they do not exist"""
        try:
            connection = mysql.connector.connect(
                host = Config.DB_HOST,
                user = Config.DB_USER,
                password = Config.DB_PASSWORD
            )
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            cursor.close()
            connection.close()


            # Creating database table
            connection = self.create_connection()
            cursor = connection.cursor()

            create_flashcards_table ="""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                topic VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium'
            )
            """

            create_study_sessions_table = """
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_name VARCHAR(255) NOT NULL,
                original_text LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            cursor.execute(create_flashcards_table)
            cursor.execute(create_study_sessions_table)
            connection.commit()
            cursor.close()
            connection.close()

            print("Database initialized successfully!")

        except Error as e:
            print(f"Error initializing database: {e}")

    def save_flashcard(self, question, answer, topic='General', difficulty='medium'):
        """Saving a flash card to the database"""
        try:
            connection = self.create_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO flashcards (question, answer, topic, difficulty)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (question, answer, topic, difficulty))
            connection.commit()

            flashcard_id = cursor.lastrowid
            cursor.close()
            connection.close()

            return flashcard_id

        except Error as e:
            print(f"Error saving flashcard: {e}")
            return None