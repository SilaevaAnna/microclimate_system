# db_connection.py
import sqlite3
import os
from typing import Optional
from ..config import Config


def get_db_connection() -> sqlite3.Connection:
    """Get database connection with proper error handling"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', Config.DATABASE_PATH)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


def execute_query(query: str, params: tuple = (), fetch_one: bool = False, fetch_all: bool = False) -> Optional[dict]:
    """Execute database query with error handling"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        
        conn.commit()
        return None
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Query execution failed: {e}")
    finally:
        if conn:
            conn.close()
