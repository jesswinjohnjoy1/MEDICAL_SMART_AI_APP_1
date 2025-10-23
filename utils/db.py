# utils/db.py
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = "data/smartai.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        secret_question TEXT,
        secret_answer TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        role TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        filename TEXT NOT NULL,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rag_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        query TEXT NOT NULL,
        answer TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        session_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)


    conn.commit()
    conn.close()

# ---------------------------
# USER FUNCTIONS
# ---------------------------
def add_user(username, password, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash, secret_question, secret_answer) VALUES (?, ?, ?, ?)",
                   (username, password_hash, question, answer))
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def check_password(username, password):
    user = get_user(username)
    return user and check_password_hash(user["password_hash"], password)

def update_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=? WHERE username=?",
                   (generate_password_hash(new_password), username))
    conn.commit()
    conn.close()

# ---------------------------
# CHAT FUNCTIONS
# ---------------------------
def save_chat(username, message, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (username, message, role) VALUES (?, ?, ?)",
                   (username, message, role))
    conn.commit()
    conn.close()

def load_chats(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE username=? ORDER BY timestamp", (username,))
    return cursor.fetchall()

def clear_chats(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ---------------------------
# RAG HISTORY FUNCTIONS
# ---------------------------
def save_rag_history(username, query, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rag_history (username, query, answer) VALUES (?, ?, ?)",
                   (username, query, answer))
    conn.commit()
    conn.close()

def get_rag_history(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rag_history WHERE username=? ORDER BY timestamp DESC", (username,))
    return cursor.fetchall()

def clear_rag_history(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rag_history WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ========================
# CHAT SESSION FUNCTIONS
# ========================
def create_chat_session(username, session_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_sessions (username, session_name) VALUES (?, ?)", (username, session_name))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def get_chat_sessions(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_sessions WHERE username=? ORDER BY created_at DESC", (username,))
    return cursor.fetchall()

def delete_chat_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE session_id=?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()

# ========================
# CHAT MESSAGES FUNCTIONS (UPDATED)
# ========================
def save_chat(session_id, username, message, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (username, message, role, session_id) VALUES (?, ?, ?, ?)",
                   (username, message, role, session_id))
    conn.commit()
    conn.close()

def load_chats_for_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE session_id=? ORDER BY timestamp", (session_id,))
    return cursor.fetchall()

