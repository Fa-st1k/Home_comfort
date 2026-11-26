
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "home_comfort.db"

class Database:
    @staticmethod
    def connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @classmethod
    def initialize(cls):
        with cls.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'client' CHECK(role IN ('client','admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL, last_name TEXT NOT NULL,
                patronymic TEXT DEFAULT '', age INTEGER NOT NULL CHECK(age BETWEEN 14 AND 100),
                position TEXT NOT NULL, experience TEXT DEFAULT '', employee_code TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL, last_name TEXT NOT NULL,
                patronymic TEXT DEFAULT '', age INTEGER NOT NULL CHECK(age BETWEEN 14 AND 100),
                position TEXT NOT NULL, experience TEXT DEFAULT '', employee_code TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE, price INTEGER NOT NULL CHECK(price >= 0),
                image TEXT DEFAULT '', available INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER REFERENCES accounts(id),
                total INTEGER NOT NULL CHECK(total >= 0),
                payment_method TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_name TEXT NOT NULL, price INTEGER NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0)
            );
            """)
            # Add missing demo products without duplicating or overwriting existing menu rows.
            db.executemany("INSERT OR IGNORE INTO menu(name,price,image) VALUES(?,?,?)", [
                ("Капучино",150,"images/cappuccino.png"),
                ("Американо",120,"images/americano.png"),
                ("Эспрессо",80,"images/espresso.png"),
                ("Чизкейк",100,"images/cheesecake.png"),
                ("Крем-суп",250,"images/soup.png"),
                ("Круассан",130,"images/croissant.png")])
