"""Database configuration"""
import psycopg2
import psycopg2.extras
from config import Config


class DatabaseManager:
    """Handles PostgreSQL database connections and queries."""

    def __init__(self):
        self.database_url = Config.DATABASE_URL

    def create_connection(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None

    def initialize_database(self):
        """Create required tables if they do not exist"""
        try:
            conn = self.create_connection()
            cursor = conn.cursor()

            create_flashcards_table = """
            CREATE TABLE IF NOT EXISTS flashcards (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                topic VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                difficulty VARCHAR(10) DEFAULT 'medium'
            )
            """

            create_study_sessions_table = """
            CREATE TABLE IF NOT EXISTS study_sessions (
                id SERIAL PRIMARY KEY,
                session_name VARCHAR(255) NOT NULL,
                original_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            cursor.execute(create_flashcards_table)
            cursor.execute(create_study_sessions_table)
            conn.commit()

            cursor.close()
            conn.close()
            print("PostgreSQL database initialized successfully!")

        except Exception as e:
            print(f"Error initializing PostgreSQL database: {e}")

    def save_flashcard(self, question, answer, topic='General', difficulty='medium'):
        """Save a flashcard and return its ID"""
        try:
            conn = self.create_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO flashcards (question, answer, topic, difficulty)
            VALUES (%s, %s, %s, %s) RETURNING id
            """
            cursor.execute(query, (question, answer, topic, difficulty))
            flashcard_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            return flashcard_id

        except Exception as e:
            print(f"Error saving flashcard: {e}")
            return None

    def get_all_flashcards(self, topic=None):
        """Retrieve flashcards, optionally filtered by topic"""
        try:
            conn = self.create_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            if topic:
                query = "SELECT * FROM flashcards WHERE topic = %s ORDER BY created_at DESC"
                cursor.execute(query, (topic,))
            else:
                query = "SELECT * FROM flashcards ORDER BY created_at DESC"
                cursor.execute(query)

            flashcards = cursor.fetchall()
            cursor.close()
            conn.close()

            # Convert to list of dicts
            return [dict(row) for row in flashcards]

        except Exception as e:
            print(f"Error retrieving flashcards: {e}")
            return []

    def save_study_session(self, session_name, original_text):
        """Save a study session and return its ID"""
        try:
            conn = self.create_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO study_sessions (session_name, original_text)
            VALUES (%s, %s) RETURNING id
            """
            cursor.execute(query, (session_name, original_text))
            session_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            return session_id

        except Exception as e:
            print(f"Error saving study session: {e}")
            return None
