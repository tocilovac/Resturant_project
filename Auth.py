# auth.py
import sqlite3
from typing import Optional, Tuple
from Database import get_connection

# NOTE: For a real app, hash passwords! This demo uses plain text for simplicity.

def register_user(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "Username and password are required."
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists."

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True, "Registration successful."

def login_user(username: str, password: str) -> Tuple[bool, str, Optional[int]]:
    if not username or not password:
        return False, "Username and password are required.", None

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    row = c.fetchone()
    conn.close()

    if row:
        return True, "Login successful.", int(row[0])
    return False, "Invalid username or password.", None

def get_user_id_by_username(username: str) -> Optional[int]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else None
