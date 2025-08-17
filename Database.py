import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "restaurant.db"


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["col_name"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create required tables if they don't exist."""
    schema = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS burgers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL CHECK (price >= 0),
        stock INTEGER NOT NULL CHECK (stock >= 0),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
        status TEXT NOT NULL DEFAULT 'confirmed',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        burger_id INTEGER NOT NULL,
        qty INTEGER NOT NULL CHECK (qty > 0),
        price_at_order REAL NOT NULL CHECK (price_at_order >= 0),
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (burger_id) REFERENCES burgers(id) ON DELETE RESTRICT
    );

    -- helpful indexes
    CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id);
    CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id);
    CREATE INDEX IF NOT EXISTS idx_order_items_burger_id ON order_items (burger_id);
    """
    with get_connection() as conn:
        conn.executescript(schema)


def seed_burgers_if_empty() -> None:
    """Add 10 burgers if the burgers table is empty."""
    burgers = [
        ("classic burger", 7.50, 25),
        ("cheeseburger", 7.90, 25),
        ("double cheeseburger", 9.49, 20),
        ("bacon burger", 8.99, 20),
        ("BBQ burger", 8.79, 18),
        ("mushroom swiss", 8.49, 18),
        ("spicy jalapeno", 8.29, 15),
        ("veggie burger", 7.99, 15),
        ("chicken burger", 8.19, 20),
        ("deluxe burger", 10.49, 12),
    ]
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM burgers")
        if cur.fetchone()["cnt"] == 0:
            conn.executemany(
                "INSERT INTO burgers (name, price, stock) VALUES (?, ?, ?)",
                burgers,
            )


if __name__ == "__main__":
    init_db()
    seed_burgers_if_empty()
    print(f"database initialized at {DB_PATH}")
