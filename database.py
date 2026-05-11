"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

# ========== КОНФИГУРАЦИЯ ==========
DB_FOLDER = "db"
DB_NAME = "echomarket.db"
DB_PATH = Path(__file__).parent / DB_FOLDER / DB_NAME

def get_db_connection():
    """Подключение к базе данных"""
    # Создаём папку если её нет
    Path(DB_FOLDER).mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Хеширование пароля (SHA-256)"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Инициализация базы данных (создание таблиц)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            rating REAL DEFAULT 0,
            ads_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица объявлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            views INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Таблица сессий (для токенов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========

def create_user(name: str, email: str, phone: str, password: str) -> dict:
    """Создание нового пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (name, email.lower(), phone, password_hash))
        conn.commit()

        user_id = cursor.lastrowid

        return {
            'success': True,
            'user_id': user_id,
            'name': name,
            'email': email,
            'phone': phone
        }
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'Пользователь с таким email уже существует'}
    finally:
        conn.close()

def login_user(email: str, password: str) -> dict:
    """Проверка логина и пароля"""
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)
    cursor.execute('''
        SELECT id, name, email, phone, rating
        FROM users 
        WHERE email = ? AND password_hash = ?
    ''', (email.lower(), password_hash))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'rating': user['rating']
            }
        }
    return {'success': False, 'error': 'Неверный email или пароль'}

def get_user_by_id(user_id: int) -> dict:
    """Получение пользователя по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, email, phone, rating, ads_count, created_at
        FROM users WHERE id = ?
    ''', (user_id,))

    user = cursor.fetchone()
    conn.close()

    if user:
        return dict(user)
    return None

def get_user_by_email(email: str) -> dict:
    """Получение пользователя по email"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, email, phone, rating, ads_count, created_at
        FROM users WHERE email = ?
    ''', (email.lower(),))

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None

def generate_token() -> str:
    """Генерация уникального токена для сессии"""
    return secrets.token_urlsafe(32)

def create_session(user_id: int) -> str:
    """Создание сессии для пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()

    token = generate_token()
    expires_at = datetime.now() + timedelta(days=7)

    cursor.execute('''
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))

    conn.commit()
    conn.close()
    return token

def get_user_by_token(token: str) -> dict:
    """Получение пользователя по токену сессии"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id, u.name, u.email, u.phone, u.rating
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    ''', (token,))

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None

def delete_session(token: str):
    """Удаление сессии (выход)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()

def get_all_users() -> list:
    """Получение всех пользователей (для админки)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, email, phone, rating, ads_count, created_at FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return users

def get_stats() -> dict:
    """Получение статистики"""
    conn = get_db_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) as count FROM users')
    stats['users'] = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM ads')
    stats['ads'] = cursor.fetchone()['count']

    conn.close()

    return stats

# Инициализация БД при импорте
init_db()