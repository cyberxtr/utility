import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'bot.db'


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                FOREIGN KEY(parent_id) REFERENCES category(id)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS file (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                telegram_file_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES category(id)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriber (
                id INTEGER PRIMARY KEY
            );
            """
        )
        conn.commit()


def add_category(name: str, parent_id=None) -> int:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO category (name, parent_id) VALUES (?, ?)",
            (name, parent_id),
        )
        conn.commit()
        return cur.lastrowid


def get_categories(parent_id=None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM category WHERE parent_id IS ?",
            (parent_id,),
        )
        return cur.fetchall()


def add_file(category_id: int, telegram_file_id: str, file_name: str) -> int:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO file (category_id, telegram_file_id, file_name) VALUES (?, ?, ?)",
            (category_id, telegram_file_id, file_name),
        )
        conn.commit()
        return cur.lastrowid


def get_files(category_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT telegram_file_id, file_name FROM file WHERE category_id = ?",
            (category_id,),
        )
        return cur.fetchall()


def add_subscriber(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO subscriber (id) VALUES (?)",
            (user_id,),
        )
        conn.commit()


def get_subscribers():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM subscriber")
        return [row[0] for row in cur.fetchall()]

