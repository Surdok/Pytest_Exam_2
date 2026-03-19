import sqlite3
import os

DB_NAME = "bookstore.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the books table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            in_stock BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_book(title, author, price):
    """
    Add a new book to the store.
    Raises ValueError if title/author empty or price <= 0.
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    if not author or not author.strip():
        raise ValueError("Author cannot be empty")
    if price <= 0:
        raise ValueError("Price must be positive")

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
        (title.strip(), author.strip(), price),
    )
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id


def get_all_books():
    """Get all books ordered by title."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_book(book_id):
    """Get a single book by ID. Returns None if not found."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_book(book_id, title=None, author=None, price=None):
    """
    Update a book's details. Only provided fields are changed.
    Raises ValueError if book not found or price <= 0.
    """
    book = get_book(book_id)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    if price is not None and price <= 0:
        raise ValueError("Price must be positive")

    conn = get_connection()
    conn.execute(
        "UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?",
        (
            title.strip() if title else book["title"],
            author.strip() if author else book["author"],
            price if price is not None else book["price"],
            book_id,
        ),
    )
    conn.commit()
    conn.close()
    return True


def delete_book(book_id):
    """Delete a book by ID. Raises ValueError if not found."""
    book = get_book(book_id)
    if book is None:
        raise ValueError(f"Book {book_id} not found")
    conn = get_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True


def search_books(query):
    """Search books by title or author (partial match)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
