# cache_manager.py
# Black-formatted code.

import sqlite3
import logging
from typing import Optional
from config import settings


class CacheManager:
    """Handles caching of question-answer pairs in an SQLite database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self._create_table()
            logging.info(f"Successfully connected to cache database at {db_path}")
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {e}", exc_info=True)

    def _create_table(self):
        """Creates the cache table if it doesn't already exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS qa_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to create cache table: {e}")

    def get_answer(self, question: str) -> Optional[str]:
        """Retrieves a cached answer for a given question."""
        if not self.conn:
            return None

        # Normalize the question to improve cache hits
        normalized_question = question.lower().strip()
        sql = "SELECT answer FROM qa_cache WHERE question = ?;"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (normalized_question,))
            result = cursor.fetchone()
            if result:
                logging.info(f"Cache HIT for question: '{question}'")
                return result[0]
            else:
                logging.info(f"Cache MISS for question: '{question}'")
                return None
        except sqlite3.Error as e:
            logging.error(f"Failed to query cache: {e}")
            return None

    def add_answer(self, question: str, answer: str):
        """Adds a new question-answer pair to the cache."""
        if not self.conn:
            return

        normalized_question = question.lower().strip()
        sql = "INSERT INTO qa_cache (question, answer) VALUES (?, ?);"
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (normalized_question, answer))
            self.conn.commit()
            logging.info(f"Cached new answer for question: '{question}'")
        except sqlite3.IntegrityError:
            # This can happen if another process caches the same question. It's safe to ignore.
            logging.warning(f"Question already exists in cache: '{question}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to insert into cache: {e}")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Cache database connection closed.")